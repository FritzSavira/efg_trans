# DEV_TASKS-0004: Manual Voice Selection (Speaker Identity)

This task involves implementing a manual voice selection feature that allows users to choose between "Auto-Detect", "Male", and "Female" voices for the translation output. This addresses the "voice sticking" issue in multi-speaker environments.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome. This iterative process is crucial for maintaining quality and correctness.

**Briefing Documents:**
*   [ADR-0004: Manual Voice Selection (Speaker Identity)](../../docs/adr/ADR-0004-manual-voice-selection.md)
*   [DEV_SPEC-0004: Manual Voice Selection (Speaker Identity)](../../docs/tasks/DEV_SPEC-0004-manual-voice-selection.md)
*   [DEV_TECH_DESIGN-0004: Technical Specification](../../docs/tasks/DEV_TECH_DESIGN-0004-manual-voice-selection.md)
*   [CODING_STYLE.md](../../docs/CODING_STYLE.md)

---

## Phase 1: Frontend UI Implementation

*Goal: Add the voice selection dropdown and manage its state.*

- [x] **Step 1.1: Add the Voice Selection Dropdown to HTML**
    - [x] **Action:** Modify `static/index.html` to include a third column in the language selection row for the Voice dropdown. Use the IDs and values specified in the Tech Design.
    - [x] **Verification (Visual Test):**
        1.  Open the application in a browser.
        2.  **Expected Result:** You should see a new dropdown labeled "Stimme:" with options "Auto-Erkennung", "Männlich", and "Weiblich".

- [x] **Step 1.2: Initialize the Dropdown in JavaScript**
    - [x] **Action:** Update the `<script>` section in `static/index.html` to create a constant for `voiceSelect` using `document.getElementById('voice-select')`.
    - [x] **Verification:** No visual change, but check the browser console for any "Element not found" errors.

- [x] **Step 1.3: Implement UI Locking Logic**
    - [x] **Action:** Update `startRecording` and `stopRecording` (and `connectWebSocket` for file uploads) in `static/index.html` to disable the `voiceSelect` dropdown when a connection is active and re-enable it when disconnected. (Update: User requested live-switching, so selectors remain enabled).
    - [x] **Verification (Interactive Test):**
        1.  Click "Start Recording".
        2.  Check if the "Stimme" dropdown is enabled.
        3.  **Report Result:** Live switching enabled.

---

## Phase 2: Protocol Extension (WebSocket & API)

*Goal: Pass the selected voice parameter from the frontend to the backend.*

- [x] **Step 2.1: Update WebSocket URL in Frontend**
    - [x] **Action:** Modify `connectWebSocket` and `startRecording` in `static/index.html` to read the current value of `voiceSelect` and append it as a query parameter `&voice=` to the WebSocket URL.
    - [x] **Verification:** No immediate change visible, will be verified in the next step.

- [x] **Step 2.2: Update Backend API Endpoint**
    - [x] **Action:** Modify the `websocket_endpoint` signature in `src/api/main.py` to accept the `voice` parameter (type `str`, default `"auto"`).
    - [x] **Action:** Add a log message in `websocket_endpoint` to print the received `voice` parameter.
    - [x] **Verification (Interactive Test):**
        1.  Start the server.
        2.  In the browser, select "Männlich" and click "Start Recording".
        3.  Check the server terminal logs.
        4.  **Expected Result:** You should see a log entry similar to: `Client connected... Voice: male`.
        5.  Repeat for "Weiblich".
        6.  **Report Result:** Confirmed.

---

## Phase 3: Backend Logic & Model Integration

*Goal: Map the voice string to a speaker ID and update the translation engine.*

- [x] **Step 3.1: Update TranslatorEngine.translate Signature**
    - [x] **Action:** Modify the `translate` method in `src/core/translator_engine.py` to accept the `voice` parameter.
    - [x] **Action:** Update the `loop.run_in_executor` call in `src/api/main.py` to pass the `voice` parameter from the endpoint to the `translate` method.
    - [x] **Verification:** Run the application. It should start without errors, though the voice won't change yet.

- [x] **Step 3.2: Implement Mapping Logic**
    - [x] **Action:** In `src/core/translator_engine.py`, add mapping that returns `12` for `"male"`, `7` for `"female"`.
    - [x] **Action:** Call this mapping method inside `translate`.
    - [x] **Verification:** Add a log in `translate` to show the mapped `speaker_id`. Verify in server logs during a recording session.

- [x] **Step 3.3: Integrate with Model Generation**
    - [x] **Action:** Update the `self.model.generate` call in `src/core/translator_engine.py` to include the `speaker_id` parameter, passing the value obtained from the mapping.
    - [x] **Verification (Interactive Test):**
        1.  Start a recording session with "Männlich" selected.
        2.  Speak a sentence.
        3.  Start a recording session with "Weiblich" selected.
        4.  Speak the same sentence.
        5.  **Expected Result:** The two output audios should have distinctly different (male vs female) voices.
        6.  **Report Result:** Confirmed.

---

## Phase 4: Quality Assurance & Documentation

*Goal: Ensure code quality and update tests.*

- [x] **Step 4.1: Code Formatting and Linting**
    - [x] **Action:** Run `black .` and `ruff check .` on the project.
    - [x] **Verification:** Ensure no formatting or linting errors remain.

- [x] **Step 4.2: Update Unit/Integration Tests**
    - [x] **Action:** Update `test_translate.py` (or create a new test) to verify that the `translate` method correctly handles the `voice` parameter without crashing.
    - [x] **Verification:** Run `pytest test_translate.py`.
    - [x] **Expected Result:** All tests pass.

- [x] **Step 4.3: Final Documentation Review**
    - [x] **Action:** Ensure `ADR-0004` and `DEV_SPEC-0004` are up-to-date with any minor implementation details discovered during development.
    - [x] **Verification:** Final check of all documents.