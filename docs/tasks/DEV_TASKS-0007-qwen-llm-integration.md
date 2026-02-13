# DEV_TASKS-0007: Qwen2.5-7B-Instruct Integration

This task covers the implementation of the Qwen2.5-7B-Instruct LLM engine for the translation pipeline.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome.

**Briefing Documents:**
*   [ADR-0007: Qwen LLM Integration](../../docs/adr/ADR-0007-qwen-llm-integration.md)
*   [DEV_SPEC-0007: Requirements Analysis](../../docs/tasks/DEV_SPEC-0007-qwen-llm-integration.md)
*   [DEV_TECH_DESIGN-0007: Technical Specification](../../docs/tasks/DEV_TECH_DESIGN-0007-qwen-llm-integration.md)

---

## Phase 1: Engine Implementation

*Goal: Create and verify the QwenEngine class.*

- [ ] **Step 1.1: Create `src/core/llm/qwen_engine.py`**
    - [ ] **Action:** Implement the `QwenTranslator` class following the tech design.
    - [ ] **Verification:** Run a lint check: `ruff check src/core/llm/qwen_engine.py`.

- [ ] **Step 1.2: Add Unit Test**
    - [ ] **Action:** Create `tests/test_qwen_engine.py` to test the `translate` method (mocking `llama-cpp` if necessary, or using a real model if available).
    - [ ] **Verification:** Run `pytest tests/test_qwen_engine.py`.

## Phase 2: Configuration and Orchestration

*Goal: Integrate the new engine into the application workflow.*

- [ ] **Step 2.1: Update `src/core/config.py`**
    - [ ] **Action:** Add support for `llm_type` and Qwen-specific configuration options.
    - [ ] **Verification:** Verify config parsing with a temporary script.

- [ ] **Step 2.2: Update Main Entry Point / Factory**
    - [ ] **Action:** Modify the engine initialization logic (likely in `src/api/main.py` or where the orchestrator is created) to select between Llama and Qwen.
    - [ ] **Verification:** Start the application with `llm_type: "qwen"` and check logs for "Loading Qwen model...".

## Phase 3: Verification and Documentation

*Goal: Ensure quality and finalize.*

- [ ] **Step 3.1: Integration Test**
    - [ ] **Action:** Run the full pipeline (ASR -> Qwen -> TTS) with a sample audio file.
    - [ ] **Verification:** Confirm the output audio contains the correct translation.

- [ ] **Step 3.2: Finalize Documentation**
    - [ ] **Action:** Update `CHANGELOG.md`.
    - [ ] **Verification:** Ensure all files are properly linked and status is updated.
