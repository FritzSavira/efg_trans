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

- [x] **Step 1.1: Add `set_min_silence` to `VADProcessor`**
    - [x] **Action:** Open `src/core/vad_processor.py`.
    - [x] **Action:** Add the `set_min_silence(self, ms: int)` method to the `VADProcessor` class.
    - [x] **Action:** Implement validation (ensure `ms` is between 100 and 5000).
    - [x] **Action:** Implement the update logic: `self.min_silence_ms = ms` and `self.iterator.min_silence_samples = ms * self.sample_rate / 1000`.
    - [x] **Action:** Add a logging statement: `logger.info(f"VAD Config Update: min_silence_duration_ms set to {ms}")`.
    - [x] **Verification:** Run `ruff check .` to ensure code style compliance.

- [x] **Step 1.2: Unit Test for Dynamic Update**
    - [x] **Action:** Open `tests/test_vad.py`.
    - [x] **Action:** Add a new test case `test_set_min_silence`.
    - [x] **Action:** In the test, instantiate `VADProcessor`, call `set_min_silence(1000)`, and assert that `vad.min_silence_ms == 1000` and `vad.iterator.min_silence_samples == 16000` (since 1000ms = 1s * 16kHz).
    - [x] **Verification:** Run `pytest tests/test_vad.py`.

---

## Phase 2: Hybrid WebSocket Protocol

*Goal: Update the API to handle both Audio (Binary) and Config (Text) messages.*

- [x] **Step 2.1: Update WebSocket Loop in `main.py`**
    - [x] **Action:** Open `src/api/main.py`.
    - [x] **Action:** Locate the `while True:` loop in `websocket_endpoint`.
    - [x] **Action:** Change `await websocket.receive_bytes()` to `await websocket.receive()`.
    - [x] **Action:** Implement the type check:
        - If `message["type"] == "websocket.receive" and "bytes" in message`: Handle as audio (existing logic).
        - If `message["type"] == "websocket.receive" and "text" in message`: Parse JSON and call `vad.set_min_silence`.
    - [x] **Action:** Add error handling (try/except) around the JSON parsing.
    - [x] **Verification:** Run the server (`docker-compose up --build`). The existing functionality (speaking) must still work. Verify by speaking a sentence.

---

## Phase 3: Frontend UI & Integration

*Goal: Provide a user interface to control the setting.*

- [x] **Step 3.1: Add Slider to `index.html`**
    - [x] **Action:** Open `static/index.html`.
    - [x] **Action:** Add a new `div` in the settings area containing:
        - A label: `<label>Antwort-Geschwindigkeit (Pause): <span id="silence-val">500 ms</span></label>`
        - A slider: `<input type="range" id="silence-slider" min="200" max="2000" step="100" value="500" class="form-range">`
    - [x] **Verification:** Reload the page. The slider should be visible.

- [x] **Step 3.2: Implement JavaScript Logic**
    - [x] **Action:** In the `<script>` section, get references to the slider and the label span.
    - [x] **Action:** Add an event listener for `input` to update the label text immediately while dragging.
    - [x] **Action:** Add an event listener for `change` (on release) to send the WebSocket message:
        ```javascript
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({type: "config", min_silence_ms: parseInt(this.value)}));
        }
        ```
    - [x] **Verification (Interactive Test):**
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

- [x] **Step 4.1: Code Cleanup**
    - [x] **Action:** Run `black .` to format all files.
    - [x] **Action:** Run `ruff check . --fix` to catch any linting errors.

- [x] **Step 4.2: Documentation**
    - [x] **Action:** Update `CHANGELOG.md` with "Added Dynamic VAD Sensitivity Slider".
    - [x] **Action:** Ensure `ADR-0003` is marked as accepted (if not already).

- [x] **Step 4.3: Final Regression Test**
    - [x] **Action:** Test the full flow: Select Language -> Adjust Slider -> Speak.
    - [x] **Verification:** Verify that language selection and speed adjustment work together without crashing the WebSocket.
