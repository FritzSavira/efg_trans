# Technical Design: Voice Cloning (Speaker Adaptation)

**Version:** 1.0
**Date:** 2026-02-10
**Author:** Gemini
**Related Documents:** [ADR-0005](docs/adr/ADR-0005-voice-cloning-integration.md), [DEV_SPEC-0005](docs/tasks/DEV_SPEC-0005-voice-cloning-integration.md)

---

### 1. Introduction

This document describes the technical implementation of Voice Cloning for SeamlessM4T v2. It focuses on extracting speaker embeddings from input audio and using them to condition the speech generation process.

---

### 2. System Architecture and Components

#### 2.1. Component Overview

*   **Inference Layer (`translator_engine.py`):**
    *   New method `get_speaker_embedding(audio_np)`: Uses the model's processor and encoder to generate a 1D tensor representing the speaker.
    *   Updated `translate()`: If `voice="clone"`, it extracts embeddings from the current segment (dynamic) or uses a cached session embedding (calibrated).

*   **API Layer (`main.py`):**
    *   Handle a new command/parameter for "calibration" via WebSocket.

#### 2.2. Embedding Extraction Flow

SeamlessM4T v2 uses a specific workflow for voice cloning:
1.  Preprocess reference audio using `processor(audio=...)`.
2.  Pass processed features to `model.generate` using the `spkr_cond_input` argument.

---

### 3. Data Model Specification

*   **Speaker Embedding:** A torch tensor (usually of size [1, 256] or similar, depending on the model's internal bottleneck). This is stored in-memory in the `TranslatorEngine` instance for the duration of a session if calibrated.

---

### 4. Backend Specification

#### 4.1. TranslatorEngine Changes

```python
def get_speaker_embedding(self, audio_np):
    # Pre-process for speaker embedding
    # Note: SeamlessM4T v2 can take raw audio as spkr_cond_input 
    # and handles extraction internally during generate()
    pass

def translate(self, audio_np, ..., voice="auto"):
    # ...
    if voice == "clone":
        # We pass the input audio itself as the speaker conditioning
        # This is the "Zero-Shot" way
        audio_inputs["spkr_cond_input"] = audio_inputs["input_features"]
    # ...
```

---

### 5. Frontend Specification

*   **Dropdown Update:** Add `<option value="clone">Klonen (Eigene Stimme)</option>` to the `#voice-select`.
*   **Calibration UI:** 
    *   A button "🎤 Kalibrieren".
    *   When clicked, it records 5 seconds of audio, sends it to a special endpoint (or via WS), and the backend saves the resulting embedding.

---

### 6. Performance Considerations

*   **GPU Memory:** Passing additional conditioning features increases VRAM usage slightly.
*   **Latency:** The internal encoder pass for `spkr_cond_input` is efficient but adds a small overhead.
