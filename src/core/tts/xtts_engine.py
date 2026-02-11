import logging
import os
from typing import Optional
from src.core.interfaces import TTSEngine

try:
    from TTS.api import TTS
except ImportError:
    TTS = None

logger = logging.getLogger(__name__)


class XTTSEngineWrapper(TTSEngine):
    def __init__(
        self,
        model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2",
        device: str = "cuda",
    ):
        if TTS is None:
            raise ImportError("coqui-tts is not installed.")

        logger.info(f"Loading TTS model: {model_name} on {device}...")
        try:
            self.tts = TTS(model_name).to(device)
            logger.info("TTS model loaded.")
        except Exception as e:
            logger.error(f"Failed to load TTS model: {e}")
            raise

    def synthesize(self, text: str, language: str, speaker_ref_path: Optional[str] = None) -> bytes:
        if self.tts is None:
            raise RuntimeError("TTS model is not initialized.")

        if not text.strip():
            return b""

        # If no speaker_ref_path provided, we might need a default or raise error
        if speaker_ref_path is None or not os.path.exists(speaker_ref_path):
            logger.warning("No valid speaker reference path provided. Using default.")

        try:
            self.tts.tts_to_file(
                text=text,
                speaker_wav=speaker_ref_path,
                language=language,
                file_path="temp_tts_output.wav",
            )

            with open("temp_tts_output.wav", "rb") as f:
                audio_bytes = f.read()

            # Clean up
            if os.path.exists("temp_tts_output.wav"):
                os.remove("temp_tts_output.wav")

            return audio_bytes

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            raise
