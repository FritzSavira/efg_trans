# Requirements Analysis & Specification: Modular "Green-Field" Pipeline (The Modular Trinity)

This document details the requirements for the re-architecture of the S2S translation system, transitioning from a monolithic End-to-End model to a modular pipeline as described in **ADR-0006**.

---

### 1. Detailed Requirements Specification

The objective is to build a local, privacy-preserving Speech-to-Speech translation system optimized for **Christian church services**. The new architecture separates the concerns of hearing (ASR), understanding/translating (LLM), and speaking (TTS) to maximize semantic accuracy and voice fidelity.

#### 1.1. Architecture & Components
The system shall be implemented as a modular pipeline ("The Modular Trinity") with the following distinct components:

*   **ASR Module (Core/ASR):**
    *   **Engine:** `Faster-Whisper` (Variant: `large-v3-turbo` for balance of speed/accuracy).
    *   **Input:** Raw audio chunks (16kHz, float32).
    *   **Output:** Transcribed text with high fidelity.
    *   **Requirement:** Must handle VAD (Voice Activity Detection) triggers effectively to segment speech.

*   **LLM Module (Core/LLM):**
    *   **Engine:** `Llama-3-8B-Instruct` (Quantization: 4-bit / GGUF via `llama.cpp` python bindings).
    *   **Function:** Translate text and apply theological corrections.
    *   **Configuration:** Must support **System Prompts** (e.g., "You are a theological translator...") and optional **Glossary/RAG** injection.
    *   **Requirement:** Strict adherence to context; zero "chat" output (no "Sure, here is the translation...").

*   **TTS Module (Core/TTS):**
    *   **Engine:** `Coqui XTTS v2` (or `StyleTTS2` as fallback).
    *   **Function:** Synthesize speech in the target language.
    *   **Cloning:** Must accept a reference audio sample (< 6s) to clone the speaker's timbre.
    *   **Requirement:** Output must match the input speaker's identity significantly better than generic models (Metric: SSS > 0.75).

*   **Pipeline Orchestrator:**
    *   Manages data flow between modules using asynchronous queues.
    *   Handles VRAM resource management (e.g., potential offloading if 12GB is exceeded).

#### 1.2. Key Performance Indicators (KPIs)
The implementation must meet the following metrics defined in ADR-0006:
1.  **Latency:** < 4000ms (End-to-End).
2.  **Accuracy:** > 95% theological term correctness.
3.  **Similarity:** > 0.75 Cosine Similarity (Voice Cloning).
4.  **Hardware:** < 12 GB Total VRAM usage.
5.  **Hallucinations:** < 1 event/hour.

#### 1.3. "Green-Field" Structure
To ensure a clean implementation, the existing codebase will be archived, and a new directory structure will be established:
*   `src_legacy/` (Archived SeamlessM4T code)
*   `src/core/audio/` (I/O, VAD)
*   `src/core/asr/` (Whisper wrapper)
*   `src/core/llm/` (Llama wrapper)
*   `src/core/tts/` (XTTS wrapper)
*   `src/pipeline/` (Orchestrator)

---

### 2. User Stories & Acceptance Criteria

**Epic: Modular Pipeline Foundation**

*   **User Story 1: High-Fidelity Transcription**
    *   **As a** system, 
    *   **I want** to transcribe incoming audio using `Faster-Whisper`,
    *   **So that** the translation layer receives an accurate text representation of the sermon.
    *   **Acceptance Criteria:**
        *   Audio chunks containing speech are transcribed into text.
        *   Silence is ignored (VAD integration).
        *   Transcription errors on clear audio are < 5% (WER).
        *   GPU VRAM usage for this module is monitored and within limits (~2GB).

*   **User Story 2: Theologically Accurate Translation**
    *   **As a** church translator,
    *   **I want** the system to translate text using a context-aware LLM (`Llama-3`),
    *   **So that** biblical terms like "Grace" or "Salvation" are translated correctly according to theological standards (e.g., Luther Bible).
    *   **Acceptance Criteria:**
        *   LLM accepts a System Prompt defining the "Theological Translator" persona.
        *   Input: "The Grace of God saves us." -> Output (DE): "Die Gnade Gottes rettet uns." (Not "Anmut").
        *   Response contains *only* the translation, no conversational filler.
        *   Inference time for a standard sentence (10-15 words) is < 1000ms.

*   **User Story 3: Authentic Voice Cloning**
    *   **As a** listener,
    *   **I want** to hear the translation in a voice that resembles the original speaker (Pastor),
    *   **So that** the experience feels personal and connected, not robotic.
    *   **Acceptance Criteria:**
        *   System accepts a short reference audio file (calibration).
        *   TTS generates audio using the reference embedding.
        *   Subjective test: The generated voice allows distinguishing between a male and female reference clearly.
        *   Objective test: Speaker Similarity Score (SSS) > 0.75 on test set.

*   **User Story 4: Low-Latency Streaming Pipeline**
    *   **As a** live attendee,
    *   **I want** the translation to arrive within 4 seconds of the spoken sentence,
    *   **So that** I can follow the service in near real-time.
    *   **Acceptance Criteria:**
        *   The modules (ASR -> LLM -> TTS) are linked via async queues.
        *   The total time from VAD silence detection to audio playback start is < 4000ms.
        *   The system does not crash or block when processing continuous input.

---

### 3. Prioritization and Dependency Analysis

*   **Prioritization (MoSCoW Method):**
    *   **Must-Have (MVP):**
        *   Clean project structure setup (`src` vs `src_legacy`).
        *   Core module implementations (ASR, LLM, TTS) functioning in isolation.
        *   Basic sequential pipeline (Audio -> ASR -> LLM -> TTS -> Audio).
        *   Voice Cloning capability (XTTS integration).
    *   **Should-Have:**
        *   Streaming response from LLM to TTS to reduce latency.
        *   Advanced VRAM management (model offloading if needed).
        *   Web-Interface update to support the new "Calibration" workflow (uploading reference audio).
    *   **Could-Have:**
        *   Dynamic Glossary editing via UI.
        *   StyleTTS2 fallback for faster inference.
    *   **Won't-Have (in this increment):**
        *   Fine-tuning of the LLM.
        *   Cloud API fallbacks.

*   **Dependencies:**
    1.  **Hardware:** Availability of a GPU with at least 8GB VRAM (ideally 12GB) for testing the full pipeline.
    2.  **Libraries:** `faster-whisper`, `llama-cpp-python`, `TTS` (Coqui) or `deep-phonemizer`.
    3.  **Models:** Downloading weights for Whisper-large-v3, Llama-3-8B-GGUF, XTTS-v2.

---

### 4. Product Backlog

| ID | Epic | User Story / Task | Priority |
| :-- | :--- | :--- | :--- |
| **PB-001** | Architecture | **Refactor:** Archive `src` to `src_legacy` and create new folder structure. | **High** |
| **PB-002** | Core | **Task:** Implement `src/core/asr/whisper_engine.py` using Faster-Whisper. | **High** |
| **PB-003** | Core | **Task:** Implement `src/core/llm/llm_engine.py` using llama-cpp-python. | **High** |
| **PB-004** | Core | **Task:** Implement `src/core/tts/tts_engine.py` using Coqui XTTS v2. | **High** |
| **PB-005** | Pipeline | **Task:** Create `src/pipeline/orchestrator.py` to link components via AsyncIO queues. | **High** |
| **PB-006** | UX | **Story:** Update Frontend (WebSocket) to handle "Reference Audio" upload for XTTS cloning. | **Medium** |
| **PB-007** | Testing | **Task:** Create Integration Test measuring End-to-End Latency (KPI-1). | **Medium** |
| **PB-008** | QA | **Task:** Create "Bible Glossary" Test Set and automated validator (KPI-2). | **Low** |

---

### 5. Definition of Done (DoD)

A Product Backlog Item is considered "Done" when:

*   **Code Quality:** Strictly adheres to `CODING_STYLE.md`. No architectural violations (e.g., direct dependency between ASR and TTS).
*   **Tests:**
    *   Unit tests for the specific module (ASR/LLM/TTS) are passing.
    *   The component handles edge cases (silence, empty text, VRAM OOM) gracefully.
*   **KPI Check:** The implementation does not flagrantly violate the KPI targets (e.g., latency > 10s is a blocker).
*   **Documentation:** Docstrings are up-to-date; architectural changes are reflected in `docs/`.
*   **Cleanliness:** No commented-out code from the `legacy` system.
