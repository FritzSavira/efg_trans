import logging
import numpy as np
from src.core.interfaces import ASREngine, TranscriptionResult

try:
    from faster_whisper import WhisperModel
except ImportError:
    WhisperModel = None

logger = logging.getLogger(__name__)


class WhisperASR(ASREngine):
    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "cuda",
        compute_type: str = "float16",
    ):
        if WhisperModel is None:
            raise ImportError("faster_whisper is not installed.")

        logger.info(f"Loading Whisper model: {model_size} on {device}...")
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
            logger.info("Whisper model loaded.")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def transcribe(self, audio: np.ndarray) -> TranscriptionResult:
        if self.model is None:
            raise RuntimeError("Whisper model is not initialized.")

        # faster-whisper expects float32
        # Ensure we don't have empty audio
        if audio.size == 0:
            return TranscriptionResult("", "en", 0.0, 0.0, 0.0)

        try:
            segments, info = self.model.transcribe(audio, beam_size=5)

            # segments is a generator, force realization to get text
            segment_list = list(segments)

            full_text = ""
            start = 0.0
            end = 0.0
            avg_confidence = 0.0

            if segment_list:
                full_text = " ".join([s.text for s in segment_list]).strip()
                start = segment_list[0].start
                end = segment_list[-1].end
                # Convert logprob to prob (approx)
                avg_confidence = np.mean([np.exp(s.avg_logprob) for s in segment_list])

            return TranscriptionResult(
                text=full_text,
                language=info.language,
                confidence=float(avg_confidence),
                start_time=start,
                end_time=end,
            )

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            # Return empty result on failure to keep pipeline alive? Or raise?
            # Raising allows orchestrator to handle it.
            raise
