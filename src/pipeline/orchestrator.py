import asyncio
import logging
import time
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
    ):
        self.asr = asr
        self.llm = llm
        self.tts = tts
        self.vad = VADProcessor()

        self.audio_q = asyncio.Queue()
        self.text_q = asyncio.Queue()
        self.translation_q = asyncio.Queue()
        self.speech_q = asyncio.Queue()

        self.is_running = False
        self.speaker_ref_path: Optional[str] = None
        self.src_lang = "en"
        self.tgt_lang = "de"

    async def start(self):
        self.is_running = True
        asyncio.create_task(self._asr_worker())
        asyncio.create_task(self._llm_worker())
        asyncio.create_task(self._tts_worker())
        logger.info("Pipeline workers started.")

    async def stop(self):
        self.is_running = False
        logger.info("Pipeline workers stopping...")

    def set_speaker_reference(self, path: str):
        logger.info(f"Setting speaker reference: {path}")
        self.speaker_ref_path = path

    def set_languages(self, src: str, tgt: str):
        self.src_lang = src
        self.tgt_lang = tgt

    async def process_audio_chunk(self, chunk_bytes: bytes):
        loop = asyncio.get_event_loop()
        sentence_audio = await loop.run_in_executor(None, self.vad.process, chunk_bytes)

        if sentence_audio is not None:
            logger.info("Sentence complete detected by VAD. Pushing to ASR.")
            segment = AudioSegment(data=sentence_audio, timestamp=time.time())
            await self.audio_q.put(segment)

    async def _asr_worker(self):
        while self.is_running:
            audio_segment = await self.audio_q.get()
            try:
                if self.asr is None:
                    logger.error("ASR Engine is missing. Skipping transcription.")
                    continue

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, self.asr.transcribe, audio_segment.data)
                if result.text:
                    logger.info(f"ASR Result: {result.text}")
                    await self.text_q.put(result)
            except Exception as e:
                logger.error(f"ASR worker error: {e}")
            finally:
                self.audio_q.task_done()

    async def _llm_worker(self):
        while self.is_running:
            asr_result = await self.text_q.get()
            try:
                if self.llm is None:
                    logger.error("LLM Engine is missing. Skipping translation.")
                    continue

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self.llm.translate,
                    asr_result.text,
                    self.src_lang,
                    self.tgt_lang,
                )
                if result.translated_text:
                    logger.info(f"LLM Result: {result.translated_text}")
                    await self.translation_q.put(result)
            except Exception as e:
                logger.error(f"LLM worker error: {e}")
            finally:
                self.text_q.task_done()

    async def _tts_worker(self):
        while self.is_running:
            tl_result = await self.translation_q.get()
            try:
                if self.tts is None:
                    logger.error("TTS Engine is missing. Skipping synthesis.")
                    continue

                loop = asyncio.get_event_loop()
                audio_bytes = await loop.run_in_executor(
                    None,
                    self.tts.synthesize,
                    tl_result.translated_text,
                    self.tgt_lang,
                    self.speaker_ref_path,
                )
                if audio_bytes:
                    logger.info(f"TTS Result: {len(audio_bytes)} bytes generated.")
                    await self.speech_q.put(audio_bytes)
            except Exception as e:
                logger.error(f"TTS worker error: {e}")
            finally:
                self.translation_q.task_done()

    async def get_output(self) -> bytes:
        return await self.speech_q.get()
