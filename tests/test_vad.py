import numpy as np
from unittest.mock import MagicMock
from src.core.vad_processor import VADProcessor


def test_vad_logic_with_mock():
    # Initialize VAD
    vad = VADProcessor()

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


if __name__ == "__main__":
    test_vad_logic_with_mock()
