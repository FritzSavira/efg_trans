# DEV_TASKS-0005: Voice Cloning Integration (Speaker Adaptation)

This task involves implementing the Voice Cloning feature using SeamlessM4T v2's zero-shot speaker adaptation.

**Briefing Documents:**
*   [ADR-0005: Voice Cloning Integration](../../docs/adr/ADR-0005-voice-cloning-integration.md)
*   [DEV_SPEC-0005: Voice Cloning Specification](../../docs/tasks/DEV_SPEC-0005-voice-cloning-integration.md)
*   [DEV_TECH_DESIGN-0005: Technical Design](../../docs/tasks/DEV_TECH_DESIGN-0005-voice-cloning-integration.md)

---

## Phase 1: Frontend Preparation

- [ ] **Step 1.1: Add "Klonen" Option to UI**
    - [ ] **Action:** Update `static/index.html` to include the "Klonen" option in the `#voice-select` dropdown.
    - [ ] **Verification:** Open UI, check if "Klonen" is selectable.

---

## Phase 2: Backend Implementation (Core)

- [ ] **Step 2.1: Implement Embedding Logic in TranslatorEngine**
    - [ ] **Action:** Modify `src/core/translator_engine.py` to handle `voice="clone"`.
    - [ ] **Action:** Use the input features as `spkr_cond_input` in the `model.generate` call.
    - [ ] **Verification:** Run a translation with "clone" selected. Log the successful passing of the parameter.

- [ ] **Step 2.2: Test Audio Quality**
    - [ ] **Action:** Compare output with fixed IDs vs. Cloning.
    - [ ] **Verification:** Subjective test: Does the output voice change when different people speak?

---

## Phase 3: Calibration Feature (Advanced)

- [ ] **Step 3.1: Backend Calibration Storage**
    - [ ] **Action:** Add a `calibrated_embedding` variable to `TranslatorEngine`.
    - [ ] **Action:** Implement a method to set this embedding from a provided audio sample.

- [ ] **Step 3.2: Frontend Calibration UI**
    - [ ] **Action:** Add a "Kalibrieren" button to the UI.
    - [ ] **Action:** Implement JavaScript logic to record 5s and send it to the server.

---

## Phase 4: Finalization

- [ ] **Step 4.1: Linting & Tests**
    - [ ] **Action:** Run `ruff` and `pytest`.
- [ ] **Step 4.2: Update Documentation**
    - [ ] **Action:** Finalize ADR status to "Implemented" if successful.
