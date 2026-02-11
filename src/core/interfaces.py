from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import numpy as np


@dataclass
class AudioSegment:
    data: np.ndarray  # Float32, 16kHz
    timestamp: float  # Unix timestamp of capture
    sample_rate: int = 16000
    is_calibration: bool = False


@dataclass
class TranscriptionResult:
    text: str
    language: str  # ISO code (e.g., "en")
    confidence: float  # 0.0 - 1.0
    start_time: float
    end_time: float


@dataclass
class TranslationResult:
    original_text: str
    translated_text: str
    src_lang: str
    tgt_lang: str
    correction_applied: bool  # True if Glossary/Prompt altered terms


class ASREngine(ABC):
    @abstractmethod
    def transcribe(self, audio: np.ndarray) -> TranscriptionResult:
        pass


class LLMEngine(ABC):
    @abstractmethod
    def translate(self, text: str, src_lang: str, tgt_lang: str) -> TranslationResult:
        pass


class TTSEngine(ABC):
    @abstractmethod
    def synthesize(self, text: str, language: str, speaker_ref_path: Optional[str] = None) -> bytes:
        pass
