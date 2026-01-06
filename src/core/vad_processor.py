import torch
import numpy as np
import logging
from typing import Optional, List
from src.core.config import config

logger = logging.getLogger(__name__)


class VADProcessor:
    def __init__(self):
        # Load Silero VAD model
        self.model, utils = torch.hub.load(
            repo_or_dir="snakers4/silero-vad", model="silero_vad", force_reload=False, onnx=False
        )
        # Unpack utils to get VADIterator
        (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

        # Configuration
        self.threshold = config.get("models", {}).get("vad", {}).get("threshold", 0.5)
        self.min_silence_ms = config.get("models", {}).get("vad", {}).get("min_silence_duration_ms", 500)
        self.padding_ms = config.get("models", {}).get("vad", {}).get("padding_ms", 0)
        self.sample_rate = 16000

        # Initialize Iterator
        # VADIterator handles the "speech detected" -> "silence" state machine
        self.iterator = VADIterator(
            self.model,
            threshold=self.threshold,
            sampling_rate=self.sample_rate,
            min_silence_duration_ms=self.min_silence_ms,
        )

        # Buffers
        self.processing_buffer = np.array([], dtype=np.float32)  # For feeding the model in correct chunk sizes
        self.sentence_buffer: List[np.ndarray] = []  # For accumulating the actual audio to return
        self.is_recording = False

    def set_min_silence(self, ms: int):
        """
        Dynamically updates the VAD sensitivity (min silence duration).
        """
        if not (100 <= ms <= 5000):
            logger.warning(f"Ignored invalid min_silence_ms: {ms}")
            return

        logger.info(f"VAD Config Update: min_silence_duration_ms set to {ms}")
        self.min_silence_ms = ms
        # Update Silero iterator property
        # min_silence_samples is calculated as: ms * sample_rate / 1000
        self.iterator.min_silence_samples = int((ms * self.sample_rate) / 1000)

    def process(self, chunk_bytes: bytes) -> Optional[np.ndarray]:
        """
        Processes a chunk of audio. Returns a complete sentence as np.ndarray
        if silence is detected after speech.
        """
        chunk_np = np.frombuffer(chunk_bytes, dtype=np.float32)
        if len(chunk_np) == 0:
            return None

        # Append to processing buffer
        self.processing_buffer = np.concatenate([self.processing_buffer, chunk_np])

        WINDOW_SIZE_SAMPLES = 512

        sentence_complete = False

        while len(self.processing_buffer) >= WINDOW_SIZE_SAMPLES:
            # Extract window
            window = self.processing_buffer[:WINDOW_SIZE_SAMPLES]
            self.processing_buffer = self.processing_buffer[WINDOW_SIZE_SAMPLES:]

            chunk_torch = torch.from_numpy(window)

            # Use VADIterator
            # It returns a dict if state changes, or None
            speech_dict = self.iterator(chunk_torch, return_seconds=False)

            # "start" in dict means speech started
            if speech_dict and "start" in speech_dict:
                logger.info("VAD: Speech started.")
                self.is_recording = True
                # We might want to include some context before start, but for now strict cut.

            # Always buffer if we are recording (or maybe we buffer everything and cut later?
            # Simple approach: If inside a speech segment (or just triggered), append.)
            # VADIterator expects continuous stream. We should accumulate audio
            # while 'is_recording' is True.
            # CAUTION: 'start' might come *after* we passed the relevant chunk if we aren't careful,
            # but VADIterator returns 'start' relative to the current stream position it tracks.

            # Actually, simpler: Always accumulate to a temporary rolling buffer?
            # Let's stick to: If recording, append.
            # But the 'start' signal means the *current* chunk contains the start.

            if self.is_recording:
                self.sentence_buffer.append(window)

            # "end" in dict means speech ended
            if speech_dict and "end" in speech_dict:
                logger.info("VAD: Speech ended.")
                self.is_recording = False
                sentence_complete = True
                # The iterator resets itself automatically for the next sentence
                # We break to return the sentence immediately
                break

        if sentence_complete and self.sentence_buffer:
            full_audio = np.concatenate(self.sentence_buffer)
            self.sentence_buffer = []  # Reset buffer
            # self.iterator.reset_states() # VADIterator does this internally usually, but 'reset_states' is for hard reset
            
            # Apply Padding
            if self.padding_ms > 0:
                pad_samples = int((self.padding_ms / 1000.0) * self.sample_rate)
                silence = np.zeros(pad_samples, dtype=np.float32)
                full_audio = np.concatenate([silence, full_audio, silence])
                logger.info(f"VAD: Added {self.padding_ms}ms padding to audio.")

            return full_audio

        return None

    def reset(self):
        self.iterator.reset_states()
        self.processing_buffer = np.array([], dtype=np.float32)
        self.sentence_buffer = []
        self.is_recording = False
