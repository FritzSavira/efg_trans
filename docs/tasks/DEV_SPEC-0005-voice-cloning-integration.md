# Requirements Analysis & Specification: Voice Cloning (Speaker Adaptation)

This document details the requirements for implementing Voice Cloning (Speaker Adaptation), as described in **ADR-0005**.

---

### 1. Detailed Requirements Specification

The system currently uses either "Auto-Detect" (which is basic zero-shot preservation) or fixed speaker IDs (Male/Female). The goal is to leverage SeamlessM4T v2's ability to deeply adapt the output voice to the specific characteristics of the source speaker.

*   **R1: Voice Cloning Mode:** Add a "Voice Cloning" (or "Eigene Stimme") option to the voice selection menu.
*   **R2: Embedding Extraction:** The `TranslatorEngine` must be able to extract speaker embeddings from a given audio segment.
*   **R3: Dynamic Adaptation:** In "Voice Cloning" mode, the engine should use the current input segment to condition the output voice.
*   **R4: Calibration Feature (Should-Have):** Allow the user to "calibrate" the voice by recording a short sample, which is then used as a stable reference for the entire session.
*   **R5: Performance Stability:** Ensure that the embedding extraction does not significantly increase translation latency.

---

### 2. User Stories & Acceptance Criteria

**Epic: Personalized Voice Translation**

*   **User Story 1: Dynamic Voice Cloning**
    *   **As a preacher,** I want the translation to sound like my own voice, **so that** the congregation feels a more personal connection to the message.
    *   **Acceptance Criteria:**
        *   The UI provides a "Klonen" option in the voice dropdown.
        *   When selected, the output audio characteristics (pitch, tone) closely match the input speaker's voice.

*   **User Story 2: Stable Voice Calibration**
    *   **As a technician,** I want to record a 5-second sample of the preacher before the service, **so that** the cloned voice remains stable even if the preacher moves away from the mic or background noise occurs.
    *   **Acceptance Criteria:**
        *   The UI provides a "Stimme kalibrieren" button (optional/advanced).
        *   The system stores the resulting embedding for the duration of the WebSocket session.

---

### 3. Prioritization and Dependency Analysis

*   **Prioritization (MoSCoW Method):**
    *   **Must-Have (MVP):**
        *   Backend implementation of speaker embedding extraction.
        *   Integration of `spkr_cond_input` in the `generate` call.
        *   "Clone" option in the frontend dropdown.
    *   **Should-Have:**
        *   Calibration mode (using a fixed reference instead of dynamic per-segment).
    *   **Could-Have:**
        *   Visual indicator (waveform) during calibration.

*   **Dependencies:**
    1.  **SeamlessM4T v2 Processor:** Requires the `processor` to handle audio inputs for embedding extraction.
    2.  **Torch Device:** Embedding extraction must happen on the same device (CUDA/CPU) as the model.

---

### 4. Product Backlog

| ID | Epic | User Story / Task | Priority |
| :-- | :--- | :--- | :--- |
| T1 | Voice Cloning | Update `index.html` with "Klonen" option | Must |
| T2 | Voice Cloning | Implement `extract_speaker_embedding` in `TranslatorEngine` | Must |
| T3 | Voice Cloning | Update `translate()` to use embeddings when "clone" is selected | Must |
| T4 | Voice Cloning | Implement session-based calibration (Backend) | Should |
| T5 | Voice Cloning | Add calibration UI button and logic (Frontend) | Should |

---

### 5. Definition of Done (DoD)

*   **Code Quality:** Adheres to `docs/CODING_STYLE.md`.
*   **Performance:** Latency increase per segment is < 200ms.
*   **Verification:** Manual test confirms that the output voice changes when different people speak in "Clone" mode.
*   **Documentation:** ADR and Specs are updated.
