# Requirements Analysis & Specification: Continuous Duplex Pipeline

This document details the requirements for implementing a full-duplex synchronous translation pipeline, as described in **ADR-0002**.

---

### 1. Detailed Requirements Specification

The core objective is to transform the existing half-duplex (walkie-talkie style) translation system into a full-duplex system capable of simultaneous interpretation. This requires parallelizing input capturing, processing, and output playback.

**Functional Requirements:**
1.  **Continuous Input:** The microphone must remain active and capturing audio even while the system is playing back translated audio.
2.  **Parallel Processing:** The system must be able to translate a previously recorded sentence (Sentence A) while simultaneously recording the next sentence (Sentence B).
3.  **Non-Blocking Output:** Audio playback in the browser must not pause or interrupt the recording process.
4.  **Audio Queueing:** The frontend must implement a FIFO (First-In-First-Out) queue to manage incoming translation segments and play them sequentially without overlap.
5.  **Acoustic Isolation:** The system must assume the user is wearing headphones to avoid feedback loops (this is a usage requirement, but software should include a warning/indicator if possible).

**Non-Functional Requirements:**
1.  **Latency:** The pipeline overhead (buffering, queuing) must be minimized to keep the "Real-Time Factor" close to 1.
2.  **Concurrency:** The backend must handle simultaneous WebSocket read/write operations efficiently using `asyncio`.
3.  **Stability:** The WebSocket connection must remain stable during simultaneous bidirectional traffic.

---

### 2. User Stories & Acceptance Criteria

**Epic: Synchronous Simultaneous Translation**

*   **User Story 1: Continuous Speech Recording**
    *   **As a user,** I want to speak continuously without waiting for the translation to finish, **so that** I can deliver a speech or long explanation naturally.
    *   **Acceptance Criteria:**
        *   The "Recording" status indicator remains active while the system plays back audio.
        *   The microphone input stream is not stopped or paused when `audio.play()` is called.
        *   The VAD processor continues to generate "Speech Started" / "Speech Ended" events during playback.

*   **User Story 2: Seamless Audio Playback (Queueing)**
    *   **As a listener,** I want to hear the translated sentences in the correct order without gaps or overlaps, **so that** I can understand the full context.
    *   **Acceptance Criteria:**
        *   If the frontend receives Sentence B while Sentence A is still playing, Sentence B is added to a queue.
        *   Sentence B starts playing immediately after Sentence A finishes.
        *   No audio segment is swallowed or discarded.

*   **User Story 3: Parallel Backend Processing**
    *   **As a developer,** I want the server to process incoming audio chunks while sending out translated audio, **so that** the throughput is maximized.
    *   **Acceptance Criteria:**
        *   The WebSocket endpoint separates the "Receive Loop" (Audio Input) from the "Send Loop" (Audio Output).
        *   Long translation times for Sentence A do not block the reception of Sentence B.

*   **User Story 4: Usage Warning (Headphones)**
    *   **As a user,** I want to be reminded to use headphones, **so that** I don't cause a feedback loop where the system translates itself.
    *   **Acceptance Criteria:**
        *   A visible UI notice (e.g., an icon or text) advises the user to use headphones for "Continuous Mode".

---

### 3. Prioritization and Dependency Analysis

*   **Prioritization (MoSCoW Method):**
    *   **Must-Have (MVP):**
        *   Asyncio backend architecture (Producer/Consumer pattern).
        *   Frontend Audio Queue (FIFO).
        *   Non-blocking microphone capture in `index.html`.
    *   **Should-Have:**
        *   UI Warning for headphones.
        *   Visual indicator for "Items in Queue" (e.g., "2 sentences pending").
    *   **Could-Have:**
        *   "Interrupt" button to clear the queue and stop playback immediately.
        *   Dynamic adjustment of VAD sensitivity (Extension 1).
    *   **Won't-Have (in this increment):**
        *   Echo Cancellation (software-based) for loudspeaker usage.
        *   Streaming text output (subtitles).

*   **Dependencies:**
    1.  **WebSocket Protocol:** No changes to the protocol itself are strictly needed, but the *handling* of the protocol changes significantly.
    2.  **VAD Logic:** The existing `VADProcessor` logic (rolling buffer) is reused but must now be thread-safe or async-compatible.

---

### 4. Product Backlog

| ID | Epic | User Story / Task | Priority |
| :-- | :--- | :--- | :--- |
| **PB-01** | Sync-Trans | **Refactor Backend to Asyncio Producer-Consumer:** Split WebSocket handler into `producer` (read/VAD) and `consumer` (translate/send). | **High** |
| **PB-02** | Sync-Trans | **Frontend Audio Queue:** Implement a JavaScript queue class to manage `ArrayBuffer` playback sequentially. | **High** |
| **PB-03** | Sync-Trans | **Non-Blocking Mic Logic:** Update `index.html` to ensure `scriptProcessor` continues running during playback. | **High** |
| **PB-04** | Sync-Trans | **UI Updates:** Add "Simultaneous Mode" toggle or headphone warning. | **Medium** |
| **PB-05** | Sync-Trans | **End-to-End Test:** Verify that speaking "Sentence 1... Sentence 2" results in two distinct audio outputs in correct order. | **High** |

---

### 5. Definition of Done (DoD)

A Product Backlog Item (e.g., a User Story or a Task) is considered "Done" when all of the following criteria are met:

*   **Code Quality:** The code is written and formatted according to the guidelines in `docs/CODING_STYLE.md` (`black .`, `ruff check .`).
*   **Tests:**
    *   All new backend functions are covered by unit tests (especially the async queue logic).
    *   Manual verification confirms that speaking while listening works without interruption.
*   **Acceptance Criteria:** All acceptance criteria defined for the story have been met and manually verified in the frontend.
*   **Code Review:** The code has been reviewed by at least one other team member (or is in a reviewable state in a pull request).
*   **Merge:** The code has been successfully merged into the main development branch (e.g., `main` or `develop`).
*   **Documentation:** `ADR-0002` is marked as "Accepted".
