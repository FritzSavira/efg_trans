import logging
from src.core.interfaces import LLMEngine, TranslationResult

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)


class QwenTranslator(LLMEngine):
    """
    LLM Engine using Qwen2.5-Instruct models (GGUF format via llama-cpp-python).
    Uses the ChatML prompt format.
    """

    def __init__(
        self,
        model_path: str = "models/qwen2.5-7b-instruct-q4_k_m.gguf",
        n_ctx: int = 2048,
        n_gpu_layers: int = -1,  # -1 for all layers to GPU
    ):
        if Llama is None:
            raise ImportError("llama-cpp-python is not installed.")

        logger.info(f"Loading Qwen model from {model_path}...")
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                verbose=False,
            )
            logger.info("Qwen model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load Qwen model: {e}")
            raise

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> TranslationResult:
        if self.llm is None:
            raise RuntimeError("Qwen model is not initialized.")

        if not text.strip():
            return TranslationResult(text, "", src_lang, tgt_lang, False)

        # Qwen2.5 ChatML-style prompt template
        system_prompt = (
            f"You are a professional theological translator. "
            f"Translate the following text from {src_lang} to {tgt_lang}. "
            f"Maintain biblical accuracy and terminology. "
            f"Output ONLY the translated text without any explanations or filler."
        )

        prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{text}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        try:
            response = self.llm(
                prompt,
                max_tokens=512,
                stop=["<|im_end|>", "<|im_start|>"],
                echo=False,
                temperature=0.0,  # Deterministic for translation
            )

            translated_text = response["choices"][0]["text"].strip()

            # Clean up any potential lingering prompt artifacts
            # Qwen sometimes repeats the assistant tag if the stop token is missed
            prefixes_to_remove = ["assistant\n", "<|im_start|>assistant\n"]
            for prefix in prefixes_to_remove:
                if translated_text.startswith(prefix):
                    translated_text = translated_text[len(prefix) :].strip()

            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                src_lang=src_lang,
                tgt_lang=tgt_lang,
                correction_applied=False,
            )

        except Exception as e:
            logger.error(f"Qwen translation failed: {e}")
            raise
