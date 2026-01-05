# Requirements Analysis & Specification: Dynamic VAD Sensitivity

This document details the requirements for implementing real-time VAD (Voice Activity Detection) sensitivity adjustment, as described in **ADR-0003**.

---

### 1. Detailed Requirements Specification

The objective is to allow users to adjust the "Response Speed" of the translator dynamically during an active session. This corresponds to changing the `min_silence_duration_ms` parameter of the VAD processor.

**Functional Requirements:**
1.  **Hybrid WebSocket Protocol:** The system must support receiving both binary audio data (PCM Float32) and text/JSON control commands over the same WebSocket connection.
2.  **Runtime Configuration:** The `VADProcessor` must expose a method to update its silence threshold immediately without resetting its entire state.
3.  **Frontend Controls:** A slider UI element must be provided to select a value between 200ms (Fast) and 2000ms (Slow).
4.  **Immediate Effect:** Adjusting the slider must send a JSON command to the server, and the effect must be noticeable on the next spoken sentence.

**Non-Functional Requirements:**
1.  **Robustness:** Malformed JSON or unexpected text messages must be logged and ignored, not causing a server crash or connection drop.
2.  **Usability:** The slider should provide visual feedback on the current value (e.g., "500 ms").

---

### 2. User Stories & Acceptance Criteria

**Epic: Runtime System Configuration**

*   **User Story 1: Adjust Response Speed**
    *   **As a user,** I want to use a slider to tell the system whether I am speaking fast or slowly, **so that** the translation timing matches my speaking style.
    *   **Acceptance Criteria:**
        *   A slider labeled "Response Speed" (or similar) is visible in the UI.
        *   Dragging the slider sends a configuration update to the server.
        *   Setting the slider to "Fast" (200ms) causes the translation to start almost immediately after I stop speaking.
        *   Setting the slider to "Slow" (1500ms) allows me to pause for a second without being interrupted.

*   **User Story 2: Hybrid Protocol Handling**
    *   **As a developer,** I want the WebSocket endpoint to distinguish between audio and config data, **so that** I don't need to open a second connection.
    *   **Acceptance Criteria:**
        *   Sending binary data works as before (Audio processing).
        *   Sending JSON `{"type": "config", "min_silence_ms": 1000}` updates the VAD instance.
        *   The system logs "VAD Config Update: min_silence_duration_ms set to 1000".

---

### 3. Prioritization and Dependency Analysis

*   **Prioritization (MoSCoW Method):**
    *   **Must-Have (MVP):**
        *   Hybrid WebSocket logic in `main.py` (Text vs Binary).
        *   `set_min_silence` method in `VADProcessor`.
        *   Frontend Slider.
    *   **Should-Have:**
        *   Visual display of the current millisecond value next to the slider.
    *   **Could-Have:**
        *   "Auto-Calibration" button (starts a test wizard).
    *   **Won't-Have (in this increment):**
        *   Persisting the user's preference to `localStorage` (Session only for now).

*   **Dependencies:**
    1.  **WebSocket Endpoint:** This feature modifies the core `websocket_endpoint` in `src/api/main.py`. It should be implemented *before* the complex Asyncio-Refactoring (Extension 2) to keep the refactoring clean, OR integrated directly into the new Async structure if done in parallel. *Decision: Implement this first as it is lower complexity.*

---

### 4. Product Backlog

| ID | Epic | User Story / Task | Priority |
| :-- | :--- | :--- | :--- |
| **PB-01** | Dyn-VAD | **Backend Protocol Update:** Modify `websocket_endpoint` to handle `text` and `bytes` messages separately. | **High** |
| **PB-02** | Dyn-VAD | **VAD Update Logic:** Add `set_min_silence()` to `VADProcessor` and ensure it updates the internal iterator safely. | **High** |
| **PB-03** | Dyn-VAD | **Frontend UI:** Add Slider to `index.html` and implement `onchange` event to send JSON. | **High** |
| **PB-04** | Dyn-VAD | **Integration Test:** Verify that changing the slider actually changes the interruption behavior. | **High** |

---

### 5. Definition of Done (DoD)

A Product Backlog Item is considered "Done" when:

*   **Code Quality:** `black` and `ruff` checks pass.
*   **Tests:**
    *   Unit test added/updated for `VADProcessor.set_min_silence`.
    *   Manual verification successful.
*   **Documentation:** `ADR-0003` is accepted.
