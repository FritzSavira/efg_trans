# DEV_TASKS-0002: Continuous Duplex Pipeline

This task list outlines the steps to implement the continuous duplex (simultaneous) translation pipeline. The goal is to allow the user to speak continuously while the system processes and plays back translations in parallel.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome. This iterative process is crucial for maintaining quality.

**Briefing Documents:**
*   [ADR-0002: Continuous Duplex Pipeline](../../docs/adr/ADR-0002-continuous-duplex-pipeline.md)
*   [DEV_SPEC-0002: Requirements & Specs](../../docs/tasks/DEV_SPEC-0002-continuous-duplex-pipeline.md)
*   [DEV_TECH_DESIGN-0002: Technical Design](../../docs/tasks/DEV_TECH_DESIGN-0002-continuous-duplex-pipeline.md)

---

## Phase 1: Backend Refactoring (Async Producer-Consumer)

*Goal: Decouple the WebSocket input loop from the translation logic using `asyncio` to allow non-blocking processing.*

- [x] **Step 1.1: Create Asyncio Queue Structure in `main.py`**
    - [x] **Action:** Modify `src/api/main.py` to import `asyncio`.
    - [x] **Action:** Inside `websocket_endpoint`, instantiate `queue = asyncio.Queue()`.
    - [x] **Action:** Create two internal async functions: `input_loop(websocket, queue, vad)` and `translation_loop(websocket, queue, translator, tgt_lang)`.
    - [x] **Action:** Use `asyncio.gather` to run both loops concurrently.
    - [x] **Verification:** Run `ruff check .` to ensure no syntax errors or unused imports.

- [x] **Step 1.2: Implement Producer (`input_loop`)**
    - [x] **Action:** Move the existing `while True` loop that receives bytes into `input_loop`.
    - [x] **Action:** Instead of calling `translator.translate` directly, push the detected `sentence_audio` (numpy array) into the `queue`.
    - [x] **Action:** Handle `WebSocketDisconnect` gracefully by pushing a `None` sentinel to the queue to signal the consumer to stop.
    - [x] **Verification:** Run the server. Connect with the frontend. Speak. Check logs: Do you see "Sentence detected" and "Pushed to queue" (add log for this)? (Note: No translation will happen yet).

- [x] **Step 1.3: Implement Consumer (`translation_loop`)**
    - [x] **Action:** Implement the `while True` loop to `await queue.get()`.
    - [x] **Action:** If item is `None`, break the loop.
    - [x] **Action:** Use `asyncio.get_running_loop().run_in_executor(None, translator.translate, sentence, tgt_lang)` to run the blocking translation inference in a separate thread.
    - [x] **Action:** `await websocket.send_bytes(wav_bytes)` to send the result back.
    - [x] **Action:** Call `queue.task_done()`.
    - [x] **Verification (Interactive Test):**
        1.  Restart `docker-compose`.
        2.  Reload browser.
        3.  Speak a sentence.
        4.  **Expected Result:** You should hear the translation.
        5.  **Critical Check:** While the translation is playing (or being processed), speak a *second* short sentence immediately. Does the log show "Sentence detected" *before* the first playback finishes? (This confirms input is no longer blocked).

---

## Phase 2: Frontend Audio Queue (FIFO)

*Goal: Ensure the browser plays received audio segments sequentially without overlap, even if they arrive rapidly.*

- [x] **Step 2.1: Implement `AudioQueue` Class in `index.html`**
    - [x] **Action:** Add a JavaScript class `AudioQueue` to `static/index.html`.
    - [x] **Action:** Implement methods: `enqueue(arrayBuffer)`, `process()`, and internal state `isPlaying` (bool) and `queue` (array).
    - [x] **Action:** The `process` method should:
        1.  Return if `isPlaying` is true.
        2.  Return if `queue` is empty.
        3.  Set `isPlaying = true`.
        4.  Decode and play the next audio buffer.
        5.  On audio `ended` event, set `isPlaying = false` and call `process()` again.

- [x] **Step 2.2: Integrate Queue with WebSocket**
    - [x] **Action:** Replace the direct `playAudio(event.data)` call in `ws.onmessage` with `audioQueue.enqueue(event.data)`.
    - [x] **Verification (Interactive Test):**
        1.  Reload browser.
        2.  Speak two short sentences quickly: "Hallo." (pause) "Wie geht es dir?".
        3.  **Expected Result:** You should hear "Hello." followed immediately by "How are you?" without them playing on top of each other.

- [x] **Step 2.3: Enable Continuous Recording**
    - [x] **Action:** Modify `stopRecording()` in `index.html`. It currently disconnects the input stream.
    - [x] **Action:** Ensure that `scriptProcessor` and `input` remain connected even when audio is playing.
    - [x] **Action:** Remove any logic that might pause the recorder when `playAudio` starts.
    - [x] **Verification:** Speak a long paragraph continuously. The system should keep translating sentence by sentence without you needing to stop.

---

## Phase 3: UI Updates & Final Polish

*Goal: Inform the user about the new mode and requirements.*

- [x] **Step 3.1: Add Headphone Warning**
    - [x] **Action:** Add a visible alert or icon in `index.html` (e.g., using Bootstrap `alert-info`) stating: "🎧 Please use headphones to prevent echo."
    - [x] **Verification:** Visual check in the browser.

- [x] **Step 3.2: Code Cleanup & Documentation**
    - [x] **Action:** Remove any old "blocking" logic comments.
    - [x] **Action:** Run `black .` and `ruff check . --fix`.
    - [x] **Action:** Update `CHANGELOG.md` with the new feature "Continuous Simultaneous Translation".
    - [x] **Verification:** Run all tests (`pytest`).

---

## Final Acceptance Test

- [x] **Step 4.0: The "Interpreter" Test**
    - [x] **Action:** Put on headphones.
    - [x] **Action:** Start recording.
    - [x] **Action:** Count from 1 to 10 in German, with a short breath between each number (to trigger VAD), but do NOT wait for the English number to be spoken.
    - [x] **Example:** "Eins" (pause) "Zwei" (pause) "Drei"...
    - [x] **Expected Result:**
        - You should typically be speaking "Vier" while hearing "One" or "Two".
        - The system should eventually output all numbers up to "Ten" in English, in the correct order.
        - The input should never freeze.
