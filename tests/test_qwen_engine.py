import pytest
from unittest.mock import MagicMock, patch
from src.core.llm.qwen_engine import QwenTranslator
from src.core.interfaces import TranslationResult

@pytest.fixture
def mock_llama():
    with patch("src.core.llm.qwen_engine.Llama") as mock:
        yield mock

def test_qwen_translator_initialization(mock_llama):
    translator = QwenTranslator(model_path="dummy_path.gguf")
    mock_llama.assert_called_once_with(
        model_path="dummy_path.gguf",
        n_ctx=2048,
        n_gpu_layers=-1,
        verbose=False
    )
    assert translator.llm is not None

def test_qwen_translator_translate_empty_text(mock_llama):
    translator = QwenTranslator()
    result = translator.translate("", "en", "de")
    assert isinstance(result, TranslationResult)
    assert result.translated_text == ""

def test_qwen_translator_translate_success(mock_llama):
    # Setup mock response
    instance = mock_llama.return_value
    instance.return_value = {
        "choices": [
            {"text": "Dies ist eine Übersetzung."}
        ]
    }

    translator = QwenTranslator()
    result = translator.translate("This is a translation.", "en", "de")

    assert result.original_text == "This is a translation."
    assert result.translated_text == "Dies ist eine Übersetzung."
    assert result.src_lang == "en"
    assert result.tgt_lang == "de"

def test_qwen_translator_prompt_format(mock_llama):
    instance = mock_llama.return_value
    instance.return_value = {
        "choices": [{"text": "Gott ist gut."}]
    }

    translator = QwenTranslator()
    translator.translate("God is good.", "en", "de")

    # Get the prompt passed to the mock
    args, kwargs = instance.call_args
    prompt = args[0]

    assert "<|im_start|>system" in prompt
    assert "professional theological translator" in prompt
    assert "<|im_start|>user" in prompt
    assert "God is good." in prompt
    assert "<|im_start|>assistant" in prompt
