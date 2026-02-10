# Requirements Analysis & Specification: Manual Voice Selection (Speaker Identity)

This document details the requirements for implementing manual voice selection, as described in **ADR-0004**.

---

### 1. Detailed Requirements Specification

The system currently relies on the zero-shot speaker preservation of SeamlessM4T v2, which can lead to "voice sticking" when multiple speakers are involved. The goal is to allow users to manually choose a voice profile to ensure consistency.

*   **R1: Frontend UI Component:** A dropdown menu must be added to the main interface allowing users to select between "Auto-Detect", "Male", and "Female".
*   **R2: Protocol Extension:** The WebSocket connection protocol must be updated to transmit the `voice` preference as a query parameter or within the initial configuration message.
*   **R3: Backend Parameter Mapping:** The API layer must receive the voice parameter and map it to internal speaker identifiers or embeddings compatible with the SeamlessM4v2 model.
*   **R4: Inference Engine Integration:** The `TranslatorEngine` must be updated to pass the selected speaker ID (or reference embedding) to the `model.generate` method.
*   **R5: Default Behavior:** The system must default to "Auto-Detect" (no specific speaker ID passed) to maintain the existing zero-shot preservation functionality unless overridden.

---

### 2. User Stories & Acceptance Criteria

**Epic: Enhanced Speaker Control**

*   **User Story 1: Manual Gender Selection**
    *   **As a user,** I want to manually select a male or female voice for the translation output, **so that** the output remains consistent even if the input speaker changes or the model fails to detect the speaker correctly.
    *   **Acceptance Criteria:**
        *   The UI provides a dropdown with "Männlich" and "Weiblich" options.
        *   Selecting "Männlich" results in a consistent male-sounding output audio.
        *   Selecting "Weiblich" results in a consistent female-sounding output audio.
        *   The selection can be changed before starting a new recording session.

*   **User Story 2: Automatic Speaker Preservation**
    *   **As a user,** I want to have an "Auto-Detect" option, **so that** the model attempts to mirror my own voice characteristics (default behavior).
    *   **Acceptance Criteria:**
        *   "Auto-Erkennung" is the default selection in the dropdown.
        *   When "Auto-Erkennung" is selected, the model preserves prosody and speaker characteristics as per the original implementation.

*   **User Story 3: Visual Feedback and Locking**
    *   **As a user,** I want the voice selection to be locked while a recording is active, **so that** the voice doesn't change mid-stream which could cause processing errors.
    *   **Acceptance Criteria:**
        *   The voice dropdown is disabled while the WebSocket connection is active (Recording/File Streaming).
        *   The dropdown is re-enabled once the connection is closed.

---

### 3. Prioritization and Dependency Analysis

*   **Prioritization (MoSCoW Method):**
    *   **Must-Have (MVP):**
        *   UI Dropdown for voice selection.
        *   WebSocket protocol update to send `voice` parameter.
        *   Backend mapping of "male"/"female" to specific speaker IDs.
    *   **Should-Have:**
        *   Dynamic update of voice selection without refreshing the page (between sessions).
    *   **Could-Have:**
        *   A library of multiple specific speaker profiles (e.g., "Deep Male", "Soft Female").
    *   **Won't-Have (in this increment):**
        *   Automatic diarization (automatic speaker switching without user intervention).

*   **Dependencies:**
    1.  **SeamlessM4T v2 API:** Requires verification of which `spkr_id` or `speaker_embeddings` are most stable for fixed gender output.
    2.  **FastAPI Endpoint:** The `/ws/translate` endpoint must be modified to accept the new parameter.

---

### 4. Product Backlog

| ID | Epic | User Story / Task | Priority |
| :-- | :--- | :--- | :--- |
| T1 | Enhanced Speaker Control | Add voice selection dropdown to `index.html` | Must |
| T2 | Enhanced Speaker Control | Update JavaScript to send `voice` param in WS URL | Must |
| T3 | Enhanced Speaker Control | Update `main.py` WebSocket endpoint to receive `voice` | Must |
| T4 | Enhanced Speaker Control | Map voice strings to speaker IDs in `TranslatorEngine` | Must |
| T5 | Enhanced Speaker Control | Update `TranslatorEngine.translate()` to use `spkr_id` | Must |
| T6 | Enhanced Speaker Control | Verify voice consistency with integration tests | Must |

---

### 5. Definition of Done (DoD)

A Product Backlog Item (e.g., a User Story or a Task) is considered "Done" when all of the following criteria are met:

*   **Code Quality:** The code is written and formatted according to the guidelines in `docs/CODING_STYLE.md` (`black .`, `ruff check .`).
*   **Tests:**
    *   All new backend functions (mapping logic) are covered by unit tests.
    *   Manual verification of voice output (Male vs Female) is successful.
    *   All existing tests continue to pass.
*   **Acceptance Criteria:** All acceptance criteria defined for the story have been met and manually verified in the frontend.
*   **Code Review:** The code has been reviewed (self-review for this agent).
*   **Merge:** The code is integrated into the source files.
*   **Documentation:** Technical documentation is updated (this SPEC and the ADR).
