# DEV_TASKS-0003: Dynamic VAD Sensitivity

This task list outlines the steps to implement real-time adjustment of the Voice Activity Detection (VAD) sensitivity. The goal is to allow users to control how quickly the system detects the end of a sentence via a UI slider.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome. This iterative process is crucial for maintaining quality.

**Briefing Documents:**
*   [ADR-0003: Dynamic VAD Sensitivity](../../docs/adr/ADR-0003-dynamic-vad-sensitivity.md)
*   [DEV_SPEC-0003: Requirements & Specs](../../docs/tasks/DEV_SPEC-0003-dynamic-vad-sensitivity.md)
*   [DEV_TECH_DESIGN-0003: Technical Design](../../docs/tasks/DEV_TECH_DESIGN-0003-dynamic-vad-sensitivity.md)

---

## Phase 1: Backend Logic (VAD Processor Update)

*Goal: Enable the VAD Processor to accept configuration updates at runtime.*

- [ ] **Step 1.1: Add `set_min_silence` to `VADProcessor`**
    - [ ] **Action:** Open `src/core/vad_processor.py`.
    - [ ] **Action:** Add the `set_min_silence(self, ms: int)` method to the `VADProcessor` class.
    - [ ] **Action:** Implement validation (ensure `ms` is between 100 and 5000).
    - [ ] **Action:** Implement the update logic: `self.min_silence_ms = ms` and `self.iterator.min_silence_samples = ms * self.sample_rate / 1000`.
    - [ ] **Action:** Add a logging statement: `logger.info(f"VAD Config Update: min_silence_duration_ms set to {ms}")`.
    - [ ] **Verification:** Run `ruff check .` to ensure code style compliance.

- [ ] **Step 1.2: Unit Test for Dynamic Update**
    - [ ] **Action:** Open `tests/test_vad.py`.
    - [ ] **Action:** Add a new test case `test_set_min_silence`.
    - [ ] **Action:** In the test, instantiate `VADProcessor`, call `set_min_silence(1000)`, and assert that `vad.min_silence_ms == 1000` and `vad.iterator.min_silence_samples == 16000` (since 1000ms = 1s * 16kHz).
    - [ ] **Verification:** Run `pytest tests/test_vad.py`.

---

## Phase 2: Hybrid WebSocket Protocol

*Goal: Update the API to handle both Audio (Binary) and Config (Text) messages.*

- [ ] **Step 2.1: Update WebSocket Loop in `main.py`**
    - [ ] **Action:** Open `src/api/main.py`.
    - [ ] **Action:** Locate the `while True:` loop in `websocket_endpoint`.
    - [ ] **Action:** Change `await websocket.receive_bytes()` to `await websocket.receive()`.
    - [ ] **Action:** Implement the type check:
        - If `message["type"] == "websocket.receive" and "bytes" in message`: Handle as audio (existing logic).
        - If `message["type"] == "websocket.receive" and "text" in message`: Parse JSON and call `vad.set_min_silence`.
    - [ ] **Action:** Add error handling (try/except) around the JSON parsing.
    - [ ] **Verification:** Run the server (`docker-compose up --build`). The existing functionality (speaking) must still work. Verify by speaking a sentence.

---

## Phase 3: Frontend UI & Integration

*Goal: Provide a user interface to control the setting.*

- [ ] **Step 3.1: Add Slider to `index.html`**
    - [ ] **Action:** Open `static/index.html`.
    - [ ] **Action:** Add a new `div` in the settings area containing:
        - A label: `<label>Antwort-Geschwindigkeit (Pause): <span id="silence-val">500 ms</span></label>`
        - A slider: `<input type="range" id="silence-slider" min="200" max="2000" step="100" value="500" class="form-range">`
    - [ ] **Verification:** Reload the page. The slider should be visible.

- [ ] **Step 3.2: Implement JavaScript Logic**
    - [ ] **Action:** In the `<script>` section, get references to the slider and the label span.
    - [ ] **Action:** Add an event listener for `input` to update the label text immediately while dragging.
    - [ ] **Action:** Add an event listener for `change` (on release) to send the WebSocket message:
        ```javascript
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({type: "config", min_silence_ms: parseInt(this.value)}));
        }
        ```
    - [ ] **Verification (Interactive Test):**
        1.  Reload the page and start recording.
        2.  Open the browser console (F12) or check Docker logs.
        3.  Move the slider to **200ms**.
        4.  Speak a short sentence ("Hallo").
        5.  **Expected Result:** The translation should trigger very quickly.
        6.  Move the slider to **2000ms**.
        7.  Speak "Hallo", wait 1 second, then say "Welt".
        8.  **Expected Result:** The system should NOT interrupt you after "Hallo". It should wait and translate "Hallo Welt" as one sentence.

---

## Phase 4: Finalization

*Goal: Ensure code quality and documentation.*

- [ ] **Step 4.1: Code Cleanup**
    - [ ] **Action:** Run `black .` to format all files.
    - [ ] **Action:** Run `ruff check . --fix` to catch any linting errors.

- [ ] **Step 4.2: Documentation**
    - [ ] **Action:** Update `CHANGELOG.md` with "Added Dynamic VAD Sensitivity Slider".
    - [ ] **Action:** Ensure `ADR-0003` is marked as accepted (if not already).

- [ ] **Step 4.3: Final Regression Test**
    - [ ] **Action:** Test the full flow: Select Language -> Adjust Slider -> Speak.
    - [ ] **Verification:** Verify that language selection and speed adjustment work together without crashing the WebSocket.
