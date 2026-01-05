import soundfile as sf
from src.core.translator_engine import TranslatorEngine
from src.core.device_manager import DeviceManager
import time
import numpy as np

def test_translation():
    device_manager = DeviceManager()
    engine = TranslatorEngine(device_manager)
    
    # Generate a dummy input (1 second of a sine wave)
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    audio_input = 0.5 * np.sin(2 * np.pi * 440 * t).astype(np.float32)
    
    print("\nProcessing dummy translation (this may take several minutes on CPU)...")
    print("It will also download the SeamlessM4T model (~4GB) if not already cached.")
    
    start_time = time.time()
    
    try:
        audio_output = engine.translate(audio_input)
        elapsed = time.time() - start_time
        
        print(f"Success! Inference time: {elapsed:.2f}s")
        print(f"Output shape: {audio_output.shape}")
        
        # Save output to file using soundfile directly
        output_file = "test_output.wav"
        sf.write(output_file, audio_output, 16000)
        print(f"Result saved to '{output_file}'")
        
    except Exception as e:
        print(f"Translation failed: {e}")

if __name__ == "__main__":
    test_translation()
