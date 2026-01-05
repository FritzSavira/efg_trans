from src.core.device_manager import DeviceManager
import torch

def test_device_manager():
    manager = DeviceManager()
    print(f"Detected Device: {manager.get_device()}")
    print(f"Torch Device Object: {manager.get_torch_device()}")
    
    if torch.cuda.is_available():
        print(f"CUDA Device Name: {torch.cuda.get_device_name(0)}")

if __name__ == "__main__":
    test_device_manager()
