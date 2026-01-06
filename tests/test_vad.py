import numpy as np
from unittest.mock import MagicMock
from src.core.vad_processor import VADProcessor


def test_vad_logic_with_mock():
    # Initialize VAD
    vad = VADProcessor()
    vad.padding_ms = 0  # Force 0 for this logic test to avoid padding interference

    # MOCK the iterator to control 'start' and 'end' events
    # We don't want to test Silero's accuracy, but OUR buffering logic.
    vad.iterator = MagicMock()

    # 1. Simulate Speech Start
    # The iterator is called with a tensor.
    # Let's say the first call returns {'start': 0}
    # and subsequent calls return None (continuing speech)
    # and finally {'end': ...}

    chunk_size = 512  # matches internal window
    # Create 3 chunks.
    # Chunk 1: Start
    # Chunk 2: Continue
    # Chunk 3: End

    chunk_bytes = np.zeros(chunk_size, dtype=np.float32).tobytes()

    # Setup mock side effects
    # We need to simulate the calls inside the loop.
    # Note: 'process' might call iterator multiple times if we send large bytes.
    # But here we send exact window size for precise control.

    # Call 1: Start Speech
    vad.iterator.return_value = {"start": 0}
    res1 = vad.process(chunk_bytes)
    assert vad.is_recording is True
    assert res1 is None

    # Call 2: Continue Speech (return None or empty dict)
    vad.iterator.return_value = {}
    res2 = vad.process(chunk_bytes)
    assert vad.is_recording is True
    assert res2 is None

    # Call 3: End Speech
    vad.iterator.return_value = {"end": 0}
    res3 = vad.process(chunk_bytes)

    assert res3 is not None, "Should return audio after 'end' event"
    assert len(res3) == chunk_size * 3, f"Expected 3 chunks of audio, got {len(res3)/chunk_size} chunks"


def test_set_min_silence():
    vad = VADProcessor()
    
    # Test valid update
    vad.set_min_silence(1000)
    assert vad.min_silence_ms == 1000
    assert vad.iterator.min_silence_samples == 16000  # 1000ms * 16000Hz / 1000

    # Test invalid update (should be ignored)
    vad.set_min_silence(50)
    assert vad.min_silence_ms == 1000  # Should remain unchanged

    vad.set_min_silence(6000)
    assert vad.min_silence_ms == 1000  # Should remain unchanged


if __name__ == "__main__":
    test_vad_logic_with_mock()

