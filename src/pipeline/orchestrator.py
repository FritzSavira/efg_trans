import asyncio
import logging
import time
import uuid
import json
import os
from datetime import datetime
from typing import Optional
from src.core.interfaces import ASREngine, LLMEngine, TTSEngine, AudioSegment
from src.core.audio.vad import VADProcessor

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    def __init__(
        self,
        asr: Optional[ASREngine],
        llm: Optional[LLMEngine],
        tts: Optional[TTSEngine],
        session_id: Optional[str] = None,
    ):
        self.asr = asr
        self.llm = llm
        self.tts = tts
        self.vad = VADProcessor()

        self.audio_q = asyncio.Queue()
        self.text_q = asyncio.Queue()
        self.translation_q = asyncio.Queue()
        self.speech_q = asyncio.Queue()
        self.metrics_q = asyncio.Queue()
        self.session_q = asyncio.Queue()

        self.is_running = False
        self.speaker_ref_path: Optional[str] = None
        self.src_lang = "en"
        self.tgt_lang = "de"
        
        # Session Logging
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log_path = f"logs/sessions/session_{self.session_id}.jsonl"
        
        # Ensure directory exists immediately
        try:
            os.makedirs("logs/sessions", exist_ok=True)
            # Create/Touch file to verify permissions
            with open(self.session_log_path, "a", encoding="utf-8") as f:
                pass
            logger.info(f"Session logging initialized: {self.session_log_path}")
        except Exception as e:
            logger.error(f"Failed to initialize session log directory/file: {e}")

    async def start(self):
        self.is_running = True
        asyncio.create_task(self._asr_worker())
        asyncio.create_task(self._llm_worker())
        asyncio.create_task(self._tts_worker())
        asyncio.create_task(self._session_logger_worker())
        logger.info("Pipeline workers started.")

    async def stop(self):
        logger.info("Pipeline workers stopping. Flushing queues...")
        # Give a small window for incoming data to reach queues
        await asyncio.sleep(0.5)
        
        # Wait for queues to be empty with timeout
        try:
            await asyncio.wait_for(self.audio_q.join(), timeout=2.0)
            await asyncio.wait_for(self.text_q.join(), timeout=2.0)
            await asyncio.wait_for(self.translation_q.join(), timeout=2.0)
            await asyncio.wait_for(self.session_q.join(), timeout=2.0)
        except asyncio.TimeoutError:
            logger.warning("Timeout while waiting for queues to flush.")
        
        self.is_running = False
        logger.info("Pipeline workers stopped.")

    def set_speaker_reference(self, path: str):
        logger.info(f"Setting speaker reference: {path}")
        self.speaker_ref_path = path

    def set_languages(self, src: str, tgt: str):
        self.src_lang = src
        self.tgt_lang = tgt

    async def get_output(self) -> bytes:
        return await self.speech_q.get()

    async def _session_logger_worker(self):
        """Dedicated worker for disk I/O to avoid blocking the pipeline."""
        logger.info("Session logger worker started.")
        while self.is_running or not self.session_q.empty():
            try:
                data = await asyncio.wait_for(self.session_q.get(), timeout=1.0)
                line = json.dumps(data, ensure_ascii=False)
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._sync_write, line)
                self.session_q.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Session logger worker error: {e}")
        logger.info("Session logger worker stopped.")

    def _sync_write(self, line: str):
        with open(self.session_log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    async def process_audio_chunk(self, chunk_bytes: bytes):
        loop = asyncio.get_event_loop()
        sentence_audio = await loop.run_in_executor(None, self.vad.process, chunk_bytes)

        if sentence_audio is not None:
            logger.info("Sentence complete detected by VAD. Pushing to ASR.")
            correlation_id = str(uuid.uuid4())
            audio_duration = len(sentence_audio) / 16000.0
            
            segment = AudioSegment(
                data=sentence_audio,
                timestamp=time.time(),
                metadata={
                    "correlation_id": correlation_id, 
                    "start_time": time.time(),
                    "audio_duration_sec": round(audio_duration, 3)
                }
            )
            await self.audio_q.put(segment)

    async def _asr_worker(self):
        while self.is_running or not self.audio_q.empty():
            try:
                audio_segment = await asyncio.wait_for(self.audio_q.get(), timeout=1.0)
                try:
                    if self.asr is None:
                        continue
                    start = time.time()
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, self.asr.transcribe, audio_segment.data, self.src_lang)
                    duration = time.time() - start
                    if result.text:
                        result.metadata = audio_segment.metadata
                        result.metadata["asr_duration"] = duration
                        result.metadata["asr_confidence"] = result.confidence
                        result.metadata["asr_text"] = result.text
                        result.metadata["asr_word_count"] = len(result.text.split())
                        await self.metrics_q.put({
                            "type": "metric", "stage": "asr", "duration": duration,
                            "correlation_id": result.metadata.get("correlation_id")
                        })
                        await self.text_q.put(result)
                except Exception as e:
                    logger.error(f"ASR worker error: {e}")
                finally:
                    self.audio_q.task_done()
            except asyncio.TimeoutError:
                continue

    async def _llm_worker(self):
        while self.is_running or not self.text_q.empty():
            try:
                asr_result = await asyncio.wait_for(self.text_q.get(), timeout=1.0)
                try:
                    if self.llm is None:
                        continue
                    start = time.time()
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(None, self.llm.translate, asr_result.text, self.src_lang, self.tgt_lang)
                    duration = time.time() - start
                    if result.translated_text:
                        result.metadata = asr_result.metadata
                        result.metadata["llm_duration"] = duration
                        result.metadata["llm_text"] = result.translated_text
                        result.metadata["llm_word_count"] = len(result.translated_text.split())
                        result.metadata["src_lang"] = self.src_lang
                        result.metadata["tgt_lang"] = self.tgt_lang
                        await self.metrics_q.put({
                            "type": "metric", "stage": "llm", "duration": duration,
                            "correlation_id": result.metadata.get("correlation_id")
                        })
                        await self.translation_q.put(result)
                except Exception as e:
                    logger.error(f"LLM worker error: {e}")
                finally:
                    self.text_q.task_done()
            except asyncio.TimeoutError:
                continue

    async def _tts_worker(self):
        while self.is_running or not self.translation_q.empty():
            try:
                tl_result = await asyncio.wait_for(self.translation_q.get(), timeout=1.0)
                try:
                    if self.tts is None:
                        continue
                    start = time.time()
                    loop = asyncio.get_event_loop()
                    audio_bytes = await loop.run_in_executor(None, self.tts.synthesize, tl_result.translated_text, self.tgt_lang, self.speaker_ref_path)
                    duration = time.time() - start
                    if audio_bytes:
                        e2e_duration = time.time() - tl_result.metadata.get("start_time", time.time())
                        metadata = tl_result.metadata
                        metadata["tts_duration"] = duration
                        metadata["tts_audio_size_bytes"] = len(audio_bytes)
                        metadata["e2e_duration"] = e2e_duration
                        audio_dur = metadata.get("audio_duration_sec", 1.0)
                        metadata["rtf"] = round(e2e_duration / audio_dur, 3) if audio_dur > 0 else 0
                        metadata["timestamp"] = datetime.now().isoformat()
                        await self.metrics_q.put({"type": "metric", "stage": "tts", "duration": duration, "correlation_id": metadata.get("correlation_id")})
                        await self.metrics_q.put({"type": "metric", "stage": "e2e", "duration": e2e_duration, "correlation_id": metadata.get("correlation_id")})
                        await self.session_q.put(metadata)
                        await self.speech_q.put(audio_bytes)
                except Exception as e:
                    logger.error(f"TTS worker error: {e}")
                finally:
                    self.translation_q.task_done()
            except asyncio.TimeoutError:
                continue
