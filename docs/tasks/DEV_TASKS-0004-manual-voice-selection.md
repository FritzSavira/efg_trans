# DEV_TASKS-0004: Manual Voice Selection (Speaker Identity)

This task involves implementing a manual voice selection feature that allows users to choose between "Auto-Detect", "Male", and "Female" voices for the translation output. This addresses the "voice sticking" issue in multi-speaker environments.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome. This iterative process is crucial for maintaining quality and correctness.

**Briefing Documents:**
*   [ADR-0004: Manual Voice Selection (Speaker Identity)](../../docs/adr/ADR-0003-manual-voice-selection.md)
*   [DEV_SPEC-0004: Manual Voice Selection (Speaker Identity)](../../docs/tasks/DEV_SPEC-0004-manual-voice-selection.md)
*   [DEV_TECH_DESIGN-0004: Technical Specification](../../docs/tasks/DEV_TECH_DESIGN-0004-manual-voice-selection.md)
*   [CODING_STYLE.md](../../docs/CODING_STYLE.md)

---

## Phase 1: Frontend UI Implementation

*Goal: Add the voice selection dropdown and manage its state.*

- [ ] **Step 1.1: Add the Voice Selection Dropdown to HTML**
    - [ ] **Action:** Modify `static/index.html` to include a third column in the language selection row for the Voice dropdown. Use the IDs and values specified in the Tech Design.
    - [ ] **Verification (Visual Test):**
        1.  Open the application in a browser.
        2.  **Expected Result:** You should see a new dropdown labeled "Stimme:" with options "Auto-Erkennung", "Männlich", and "Weiblich".

- [ ] **Step 1.2: Initialize the Dropdown in JavaScript**
    - [ ] **Action:** Update the `<script>` section in `static/index.html` to create a constant for `voiceSelect` using `document.getElementById('voice-select')`.
    - [ ] **Verification:** No visual change, but check the browser console for any "Element not found" errors.

- [ ] **Step 1.3: Implement UI Locking Logic**
    - [ ] **Action:** Update `startRecording` and `stopRecording` (and `connectWebSocket` for file uploads) in `static/index.html` to disable the `voiceSelect` dropdown when a connection is active and re-enable it when disconnected.
    - [ ] **Verification (Interactive Test):**
        1.  Click "Start Recording".
        2.  Check if the "Stimme" dropdown is disabled (greyed out).
        3.  Click "Stop Recording".
        4.  Check if the "Stimme" dropdown is enabled again.
        5.  **Report Result:** Does the locking work as expected?

---

## Phase 2: Protocol Extension (WebSocket & API)

*Goal: Pass the selected voice parameter from the frontend to the backend.*

- [ ] **Step 2.1: Update WebSocket URL in Frontend**
    - [ ] **Action:** Modify `connectWebSocket` and `startRecording` in `static/index.html` to read the current value of `voiceSelect` and append it as a query parameter `&voice=` to the WebSocket URL.
    - [ ] **Verification:** No immediate change visible, will be verified in the next step.

- [ ] **Step 2.2: Update Backend API Endpoint**
    - [ ] **Action:** Modify the `websocket_endpoint` signature in `src/api/main.py` to accept the `voice` parameter (type `str`, default `"auto"`).
    - [ ] **Action:** Add a log message in `websocket_endpoint` to print the received `voice` parameter.
    - [ ] **Verification (Interactive Test):**
        1.  Start the server.
        2.  In the browser, select "Männlich" and click "Start Recording".
        3.  Check the server terminal logs.
        4.  **Expected Result:** You should see a log entry similar to: `Client connected... Voice: male`.
        5.  Repeat for "Weiblich".
        6.  **Report Result:** Are the correct values appearing in the server logs?

---

## Phase 3: Backend Logic & Model Integration

*Goal: Map the voice string to a speaker ID and update the translation engine.*

- [ ] **Step 3.1: Update TranslatorEngine.translate Signature**
    - [ ] **Action:** Modify the `translate` method in `src/core/translator_engine.py` to accept the `voice` parameter.
    - [ ] **Action:** Update the `loop.run_in_executor` call in `src/api/main.py` to pass the `voice` parameter from the endpoint to the `translate` method.
    - [ ] **Verification:** Run the application. It should start without errors, though the voice won't change yet.

- [ ] **Step 3.2: Implement Mapping Logic**
    - [ ] **Action:** In `src/core/translator_engine.py`, add a private method `_map_voice_to_id(self, voice: str)` that returns `0` for `"male"`, `1` for `"female"`, and `None` for `"auto"`.
    - [ ] **Action:** Call this mapping method inside `translate`.
    - [ ] **Verification:** Add a log in `translate` to show the mapped `speaker_id`. Verify in server logs during a recording session.

- [ ] **Step 3.3: Integrate with Model Generation**
    - [ ] **Action:** Update the `self.model.generate` call in `src/core/translator_engine.py` to include the `speaker_id` parameter, passing the value obtained from the mapping.
    - [ ] **Verification (Interactive Test):**
        1.  Start a recording session with "Männlich" selected.
        2.  Speak a sentence.
        3.  Start a recording session with "Weiblich" selected.
        4.  Speak the same sentence.
        5.  **Expected Result:** The two output audios should have distinctly different (male vs female) voices.
        6.  **Report Result:** Does the speaker gender change correctly?

---

## Phase 4: Quality Assurance & Documentation

*Goal: Ensure code quality and update tests.*

- [ ] **Step 4.1: Code Formatting and Linting**
    - [ ] **Action:** Run `black .` and `ruff check .` on the project.
    - [ ] **Verification:** Ensure no formatting or linting errors remain.

- [ ] **Step 4.2: Update Unit/Integration Tests**
    - [ ] **Action:** Update `test_translate.py` (or create a new test) to verify that the `translate` method correctly handles the `voice` parameter without crashing.
    - [ ] **Verification:** Run `pytest test_translate.py`.
    - [ ] **Expected Result:** All tests pass.

- [ ] **Step 4.3: Final Documentation Review**
    - [ ] **Action:** Ensure `ADR-0004` and `DEV_SPEC-0004` are up-to-date with any minor implementation details discovered during development.
    - [ ] **Verification:** Final check of all documents.
