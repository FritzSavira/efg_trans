# System Architecture: The Modular Trinity

This document describes the modular pipeline architecture of the S2S (Speech-to-Speech) translation system, designed for high-accuracy theological translations with authentic voice cloning.

## 1. Overview

The system follows a decoupled, asynchronous pipeline architecture consisting of three primary stages, often referred to as "The Modular Trinity":

1.  **ASR (Automatic Speech Recognition):** Hearing and transcribing.
2.  **LLM (Large Language Model):** Understanding and translating.
3.  **TTS (Text-to-Speech):** Synthesizing with voice cloning.

## 2. Component Detail

### 2.1. ASR Engine (Faster-Whisper)
- **Model:** `large-v3` (default).
- **Function:** Converts raw 16kHz mono audio into text.
- **Optimization:** Uses CTranslate2 for high-speed inference on GPU (float16).
- **VAD Integration:** Silero VAD is used to segment audio into complete sentences before transcription.

### 2.2. LLM Engine (Llama-3 / Qwen2.5)
- **Model:** Qwen2.5-7B-Instruct (GGUF, 4-bit quantization).
- **Function:** Translates transcribed text while applying theological context.
- **Configuration:** Strict ChatML prompting to ensure zero-filler output and high term accuracy.
- **Backend:** `llama-cpp-python` with full GPU offloading.

### 2.3. TTS Engine (Coqui XTTS v2)
- **Model:** XTTS v2.
- **Function:** Generates natural-sounding speech in the target language.
- **Voice Cloning:** Uses a 6-10 second reference audio sample to clone the speaker's timbre.
- **Format:** Outputs 24kHz/16kHz WAV data streamed to the client.

## 3. Pipeline Orchestration

The `PipelineOrchestrator` manages the data flow using `asyncio.Queue` objects.

### 3.1. Data Flow
`Audio Input` -> `VAD` -> `audio_q` -> **ASR Worker** -> `text_q` -> **LLM Worker** -> `translation_q` -> **TTS Worker** -> `speech_q` -> `WebSocket Output`

### 3.2. Performance Monitoring
The orchestrator tracks timestamps for every stage:
- **ASR Latency:** Time to transcribe.
- **LLM Latency:** Time to translate.
- **TTS Latency:** Time to synthesize.
- **End-to-End (E2E) Latency:** Total time from the end of speech to the beginning of audio output.

Metrics are pushed to a dedicated `metrics_q` and streamed to the frontend via WebSocket.

## 4. Logging and Analytics

### 4.1. Session Logging
Every translation session is logged into `logs/sessions/session_<ID>.jsonl`.
Each record includes:
- Source and Target text.
- Word counts.
- All stage latencies.
- **RTF (Real-Time Factor):** `E2E Latency / Input Audio Duration`.

### 4.2. Decoupling
Logging and metric reporting are decoupled from the main translation workers via separate queues and workers (`_session_logger_worker`) to ensure that disk I/O or network fluctuations do not affect the translation speed.
