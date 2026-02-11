import torch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeviceManager:
    def __init__(self):
        self.device = self._detect_device()
        logger.info(f"Device Manager initialized. Running on: {self.device}")

    def _detect_device(self) -> str:
        """
        Detects if CUDA is available and returns the device string.

        Returns:
            str: 'cuda' (or 'cuda:0') if available, otherwise 'cpu'.
        """
        if torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
        return device

    def get_device(self) -> str:
        """
        Returns the detected device.
        """
        return self.device

    def get_torch_device(self) -> torch.device:
        """
        Returns the torch.device object.
        """
        return torch.device(self.device)
