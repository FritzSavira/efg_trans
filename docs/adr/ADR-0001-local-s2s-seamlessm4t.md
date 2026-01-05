# ADR-0001: Local Speech-to-Speech Translation using SeamlessM4T

*   **Status:** Proposed
*   **Date:** 2026-01-01
*   **Deciders:** [User], Gemini Agent
*   **Technical Story:** [S2S Implementation]

## Context and Problem Statement

The project requires a Speech-to-Speech (S2S) translation system that translates German audio input into English audio output.

The key constraints and requirements are:
1.  **Simplicity & Latency:** The system should minimize the architectural complexity and latency typically associated with multi-stage pipelines (ASR -> MT -> TTS).
2.  **Prosody Preservation:** The translated audio should ideally retain the emotional tone and prosody of the speaker, which is a strength of End-to-End models.
3.  **Local Execution:** The system must run locally on a standard Windows 11 machine.
4.  **Hardware Flexibility (CPU Fallback):** While a GPU is preferred for performance, the system **must** be capable of running on a CPU-only environment for testing and development purposes.
5.  **No RAG:** A conscious decision was made to exclude Retrieval-Augmented Generation (RAG) for terminology management in this iteration to prioritize the implementation of the core S2S pipeline.

## Decision Drivers

*   Need for a functioning prototype with minimal component integration overhead.
*   Requirement to run on consumer hardware (Win 11, potential lack of CUDA GPU).
*   Desire for natural-sounding translations (prosody transfer).

## Considered Options

1.  **End-to-End (Selected):** Using Meta's SeamlessM4T v2 model.
2.  **Cascaded Pipeline:** Using Whisper (ASR) + LLM (Translation) + TTS (Synthesis).
3.  **Cloud-Native:** Using API providers (e.g., OpenAI Audio API, ElevenLabs).

## Decision Outcome

Chosen option: **End-to-End with SeamlessM4T v2**, because it offers a "Direct Pipe" architecture that simplifies the codebase and natively handles S2S tasks with prosody transfer.

### Implementation Details
*   **Model Framework:** Hugging Face `transformers` library.
*   **Model Variant:** `facebook/seamless-m4t-v2-large` (default) with configuration options to switch to `medium` if hardware constraints require it.
*   **Transport Layer:** **FastAPI** with **WebSockets** to handle audio streaming.
*   **Segmentation:** **Silero VAD** (Voice Activity Detection) will be used to detect sentence boundaries and trigger the translation process, ensuring the model receives sufficient context.
*   **Device Strategy:** The application initialization logic will automatically check for `torch.cuda.is_available()`.
    *   **If CUDA:** Load model to GPU (fp16 precision recommended).
    *   **If CPU:** Load model to CPU (float32 or quantized). The documentation must explicitly state the latency expectations when running on CPU.

## Consequences

### Positive
*   **Architecture Simplicity:** Eliminates the need to manage three separate models (ASR, MT, TTS) and their intermediate data formats.
*   **Prosody:** SeamlessM4T is capable of transferring the style of the input speech to the output.
*   **Portability:** The Python-based stack works well on Windows 11.
*   **Offline Capability:** Fully functional without internet access once models are downloaded.

### Negative
*   **Hardware Demand:** The "Large" model is VRAM/RAM intensive. Running on CPU will result in significant latency (likely >5 seconds per sentence), making "simultaneous" translation feel disjointed during testing.
*   **Lack of Control:** Without RAG, specific technical terminology cannot be forced. If the model mistranslates a technical term, there is no easy intervention point.
*   **Resource Lock:** The model requires loading a large checkpoint into memory, which might affect multitasking on smaller development machines.

## Pros and Cons of the Options

### Option 1: End-to-End (SeamlessM4T)
*   *Good:* Simple architecture, prosody transfer, single dependency.
*   *Bad:* Heavy hardware requirements, no terminology enforcement.

### Option 2: Cascaded Pipeline (Whisper -> LLM -> TTS)
*   *Good:* Modular, allows RAG integration, individual components can be swapped/optimized.
*   *Bad:* Latency accumulates at every step, "Robotic" output (loss of prosody), complex async management.

### Option 3: Cloud-Native
*   *Good:* Zero local load, high quality.
*   *Bad:* Recurring costs, privacy concerns, dependency on internet connectivity.
