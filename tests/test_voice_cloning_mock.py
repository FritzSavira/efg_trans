import unittest
from unittest.mock import MagicMock, patch
import torch
import numpy as np
import logging

# Configure logging to capture output
logging.basicConfig(level=logging.INFO)

from src.core.translator_engine import TranslatorEngine

class TestVoiceCloning(unittest.TestCase):
    @patch('src.core.translator_engine.SeamlessM4Tv2Model')
    @patch('src.core.translator_engine.AutoProcessor')
    @patch('src.core.translator_engine.DeviceManager')
    @patch('src.core.translator_engine.config')
    def test_translate_with_cloning(self, mock_config, mock_device_manager, mock_processor_cls, mock_model_cls):
        # Setup Mocks
        mock_device = MagicMock()
        mock_device.type = 'cpu'
        mock_device_manager.return_value.get_torch_device.return_value = mock_device
        
        mock_config.get.return_value = {}

        mock_processor = MagicMock()
        mock_processor_cls.from_pretrained.return_value = mock_processor

        mock_model = MagicMock()
        mock_model_cls.from_pretrained.return_value = mock_model
        # CRITICAL FIX: Ensure .to() returns the mock_model itself
        mock_model.to.return_value = mock_model

        # Mock Processor Output
        mock_inputs = {
            "input_features": torch.randn(1, 100, 80),
            "attention_mask": torch.ones(1, 100)
        }
        mock_processor_return = MagicMock()
        mock_processor.return_value = mock_processor_return
        mock_processor_return.to.return_value = mock_inputs

        # Mock Generate Output
        mock_model.generate.return_value = [torch.randn(1, 16000)]

        # Initialize Engine
        engine = TranslatorEngine(mock_device_manager())

        # Dummy Audio
        dummy_audio = np.zeros(16000, dtype=np.float32)

        # Test "clone" mode
        print("Calling translate with voice='clone'...")
        engine.translate(dummy_audio, voice="clone")
        
        # Verify
        _, kwargs = mock_model.generate.call_args
        
        self.assertIn("spkr_cond_input", kwargs)
        self.assertTrue(torch.equal(kwargs["spkr_cond_input"], mock_inputs["input_features"]))
        self.assertNotIn("speaker_id", kwargs)
        
        print("Test 'test_translate_with_cloning' passed.")

    @patch('src.core.translator_engine.SeamlessM4Tv2Model')
    @patch('src.core.translator_engine.AutoProcessor')
    @patch('src.core.translator_engine.DeviceManager')
    @patch('src.core.translator_engine.config')
    def test_translate_with_male_voice(self, mock_config, mock_device_manager, mock_processor_cls, mock_model_cls):       
        mock_device_manager.return_value.get_torch_device.return_value = MagicMock(type='cpu')
        mock_config.get.return_value = {}

        mock_processor = MagicMock()
        mock_processor_cls.from_pretrained.return_value = mock_processor
        
        mock_inputs = {"input_features": torch.tensor([1])}
        mock_processor_return = MagicMock()
        mock_processor.return_value = mock_processor_return
        mock_processor_return.to.return_value = mock_inputs

        mock_model = MagicMock()
        mock_model_cls.from_pretrained.return_value = mock_model
        # CRITICAL FIX: Ensure .to() returns the mock_model itself
        mock_model.to.return_value = mock_model

        mock_model.generate.return_value = [torch.zeros(1, 16000)]

        engine = TranslatorEngine(mock_device_manager())
        engine.translate(np.zeros(16000), voice="male")
        
        _, kwargs = mock_model.generate.call_args
        self.assertIn("speaker_id", kwargs)
        self.assertEqual(kwargs["speaker_id"], 12)
        self.assertNotIn("spkr_cond_input", kwargs)
        
        print("Test 'test_translate_with_male_voice' passed.")

if __name__ == '__main__':
    unittest.main()
