# Requirements Analysis & Specification: Qwen2.5-7B-Instruct Integration

This document details the requirements for integrating Qwen2.5-7B-Instruct as a translation engine, as described in **ADR-0007**.

---

### 1. Detailed Requirements Specification

The system must support Qwen2.5-7B-Instruct as an alternative to Llama-3 for the translation phase of the duplex pipeline.

*   **Model Support:** Must load and run `qwen2.5-7b-instruct-q4_k_m.gguf`.
*   **Prompt Engineering:** Must use the Qwen ChatML prompt format to ensure high-quality, deterministic translations.
*   **Theological Context:** The prompt must include instructions to maintain biblical accuracy and specific terminology.
*   **Performance:** Latency for a typical sentence (15-30 words) should be under 500ms on target hardware (RTX 3060 or better).
*   **Configurability:** The user must be able to select the LLM engine and model path via `config.yaml`.

---

### 2. User Stories & Acceptance Criteria

**Epic: Enhanced Multilingual Translation**

*   **User Story 1: Integration of Qwen2.5**
    *   **As a developer,** I want to use Qwen2.5-7B-Instruct as the LLM engine, **so that** I can leverage its multilingual capabilities for theological translation.
    *   **Acceptance Criteria:**
        *   `QwenEngine` class implements `LLMEngine`.
        *   The engine correctly parses and formats ChatML prompts.
        *   The engine returns a `TranslationResult` matching the interface.

*   **User Story 2: Engine Selection via Config**
    *   **As a user,** I want to switch between Llama and Qwen in the configuration, **so that** I can compare translation results easily.
    *   **Acceptance Criteria:**
        *   `config.yaml` includes a setting for `llm_type`.
        *   The orchestrator or factory initializes the correct engine based on the config.

---

### 3. Prioritization and Dependency Analysis

*   **Prioritization (MoSCoW Method):**
    *   **Must-Have (MVP):**
        *   `QwenEngine` implementation.
        *   Support for GGUF Q4_K_M.
        *   ChatML prompt template.
    *   **Should-Have:**
        *   Configuration-based engine selection.
        *   Basic unit tests for translation output.
    *   **Could-Have:**
        *   Benchmark script to compare Qwen and Llama latency.
    *   **Won't-Have (in this increment):**
        *   Dynamic engine switching without restart.

*   **Dependencies:**
    1.  **llama-cpp-python:** Must be installed (already present in the project).
    2.  **Model File:** `qwen2.5-7b-instruct-q4_k_m.gguf` must be available in the `models/` folder.

---

### 4. Product Backlog

| ID | Epic | User Story / Task | Priority |
| :-- | :--- | :--- | :--- |
| US.1 | LLM Integration | Implement `QwenEngine` class | High |
| US.2 | Configuration | Update `Config` and Orchestrator for engine selection | Medium |
| US.3 | Testing | Create `test_qwen_engine.py` | Medium |

---

### 5. Definition of Done (DoD)

A Product Backlog Item is considered "Done" when:

*   **Code Quality:** Follows `docs/CODING_STYLE.md`.
*   **Tests:** `test_qwen_engine.py` passes; integration with `orchestrator.py` verified.
*   **Functionality:** Translation via Qwen works end-to-end in the duplex pipeline.
*   **Documentation:** ADR and DEV_SPEC updated and finalized.
