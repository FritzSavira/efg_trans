import logging
from src.core.interfaces import LLMEngine, TranslationResult

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None

logger = logging.getLogger(__name__)


class LlamaTranslator(LLMEngine):
    def __init__(
        self,
        model_path: str = "models/Meta-Llama-3-8b-Instruct-Q4_K_M.gguf",
        n_ctx: int = 2048,
        n_gpu_layers: int = -1,  # -1 for all layers to GPU
    ):
        if Llama is None:
            raise ImportError("llama-cpp-python is not installed.")

        logger.info(f"Loading Llama model from {model_path}...")
        try:
            self.llm = Llama(
                model_path=model_path,
                n_ctx=n_ctx,
                n_gpu_layers=n_gpu_layers,
                verbose=False,
            )
            logger.info("Llama model loaded.")
        except Exception as e:
            logger.error(f"Failed to load Llama model: {e}")
            raise

    def translate(self, text: str, src_lang: str, tgt_lang: str) -> TranslationResult:
        if self.llm is None:
            raise RuntimeError("Llama model is not initialized.")

        if not text.strip():
            return TranslationResult(text, "", src_lang, tgt_lang, False)

        # Construct a strict prompt for translation
        # Llama-3 Instruct template
        prompt = (
            f"<|start_header_id|>system<|end_header_id|>\n\n"
            f"You are a professional theological translator. "
            f"Translate the following text from {src_lang} to {tgt_lang}. "
            f"Maintain biblical accuracy and terminology. "
            f"Output ONLY the translated text without any explanations or filler.<|eot_id|>"
            f"<|start_header_id|>user<|end_header_id|>\n\n"
            f"{text}<|eot_id|>"
            f"<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

        try:
            response = self.llm(
                prompt,
                max_tokens=512,
                stop=["<|eot_id|>"],
                echo=False,
                temperature=0.0,  # Deterministic for translation
            )

            translated_text = response["choices"][0]["text"].strip()

            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                src_lang=src_lang,
                tgt_lang=tgt_lang,
                correction_applied=False,  # Glossary logic would go here
            )

        except Exception as e:
            logger.error(f"LLM translation failed: {e}")
            raise
