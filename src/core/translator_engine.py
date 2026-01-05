import torch
import numpy as np
import logging
import io
import soundfile as sf
from transformers import AutoProcessor, SeamlessM4Tv2Model
from src.core.config import config
from src.core.device_manager import DeviceManager

logger = logging.getLogger(__name__)


class TranslatorEngine:
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
        self.device = self.device_manager.get_torch_device()

        # Load configuration
        model_cfg = config.get("models", {}).get("translation", {})
        self.model_name = model_cfg.get("variant", "facebook/seamless-m4t-v2-large")
        self.src_lang = model_cfg.get("src_lang", "deu")
        self.tgt_lang = model_cfg.get("tgt_lang", "eng")

        logger.info(f"Loading Translator Engine: {self.model_name} on {self.device}...")

        # Determine dtype based on device
        # Use float16 on GPU to save VRAM, float32 on CPU
        self.dtype = torch.float16 if self.device.type == "cuda" else torch.float32

        # Load processor and model (Explicitly use v2 class)
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = SeamlessM4Tv2Model.from_pretrained(self.model_name, torch_dtype=self.dtype).to(self.device)

        logger.info("Translator Engine loaded successfully.")

    def translate(self, audio_np: np.ndarray, tgt_lang: str = None) -> bytes:
        """
        Translates German audio input to a target language audio output.

        Args:
            audio_np (np.ndarray): Input audio (16kHz, float32).
            tgt_lang (str, optional): Target language code. Defaults to config value.

        Returns:
            bytes: Synthesized audio as WAV file (in-memory).
        """
        target = tgt_lang if tgt_lang else self.tgt_lang
        
        # DEBUG: Check input audio stats
        input_max = np.max(np.abs(audio_np))
        input_mean = np.mean(np.abs(audio_np))
        logger.info(
            f"Starting translation ({self.src_lang} -> {target})... Input Stats: Max={input_max:.4f}, Mean={input_mean:.4f}, Length={len(audio_np)} samples"
        )

        if input_max < 0.01:
            logger.warning("Input audio is extremely quiet! The model might hallucinate.")

        # Pre-process
        audio_inputs = self.processor(
            audio=audio_np, src_lang=self.src_lang, return_tensors="pt", sampling_rate=16000
        ).to(self.device)

        # Cast to correct dtype for inference
        if self.dtype == torch.float16:
            audio_inputs = {
                k: v.to(torch.float16) if torch.is_floating_point(v) else v for k, v in audio_inputs.items()
            }

        # Generate Speech
        with torch.no_grad():
            output_tokens = self.model.generate(
                **audio_inputs,
                tgt_lang=target,
                generate_speech=True
            )

        # SeamlessM4Tv2Model returns audio in output_tokens[0]
        translated_audio = output_tokens[0].cpu().numpy().squeeze()

        # Check output stats and Normalize to prevent clipping
        out_max = np.max(np.abs(translated_audio))
        logger.info(
            f"Translation complete. Generated {len(translated_audio)} samples. Output Max Amplitude: {out_max:.4f}"
        )

        if out_max > 0.0001:
            # Normalize to 0.9 range to be safe
            norm_factor = 0.9 / out_max
            translated_audio = translated_audio * norm_factor

        # Convert to WAV bytes in-memory
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, translated_audio.astype(np.float32), 16000, format="WAV")
        wav_bytes = wav_buffer.getvalue()

        return wav_bytes
