# ADR-0002: Continuous Duplex Pipeline for Simultaneous Translation

## Status
Accepted

## Date
2026-01-05

## Context
The current Speech-to-Speech (S2S) system operates in a **Half-Duplex** mode, functioning similarly to a walkie-talkie. The workflow is strictly sequential:
1.  User speaks.
2.  System detects silence (end of sentence).
3.  System blocks input, processes the translation, and plays the audio.
4.  User must wait for playback to finish before speaking again.

This "stop-and-wait" mechanism disrupts the natural flow of conversation and makes the system unsuitable for scenarios requiring continuous speech, such as interpreting a speech or a lecture. The user experience is disjointed, and the efficiency of communication is limited by the playback duration of the translation.

We need a system that allows the user to speak continuously while the system translates and plays back previous sentences in the background (**Full-Duplex**), similar to a simultaneous interpreter.

## Decision
We will transition the architecture from a sequential request-response model to a **Continuous Duplex Pipeline**.

This involves changes across the full stack:

1.  **Backend (FastAPI/Python):**
    *   We will adopt an **Asynchronous Producer-Consumer Pattern** within the WebSocket connection.
    *   The `receive` loop (Input/VAD) and the `send` loop (Output/Translation) will be decoupled into separate asynchronous tasks (using `asyncio.create_task` or `asyncio.gather`).
    *   The VAD processor will run continuously on the input stream. Detected audio segments will be pushed to an internal processing queue.
    *   A separate worker task will pull segments from the queue, perform the translation using the `TranslatorEngine`, and send the resulting audio bytes back to the client as soon as they are ready.

2.  **Frontend (JavaScript):**
    *   The microphone input stream will remain open permanently.
    *   We will implement a **Client-Side Audio Queue (FIFO)**.
    *   Incoming audio blobs (translations) will be pushed into this queue.
    *   A playback manager will monitor the queue and play audio segments sequentially. If segment B arrives while segment A is playing, B waits until A finishes. This prevents audio overlap.

3.  **Hardware Constraint:**
    *   We explicitly define **Acoustic Isolation** (e.g., usage of headphones) as a system requirement for this mode to prevent the microphone from capturing the system's audio output (echo loop).

## Consequences

### Positive
*   **Natural Conversation Flow:** The user does not need to pause for the translator, enabling a seamless "stream of consciousness" experience.
*   **Higher Throughput:** The system processes audio in parallel with user input, significantly reducing total session time.
*   **Professional Utility:** Enables use cases like live interpreting and lecture translation.

### Negative
*   **Increased Complexity:** Managing concurrency introduces risks of race conditions (though minimized by queues) and makes debugging harder.
*   **Latency accumulation:** If the speaker talks significantly faster than the translation inference time (Real-Time Factor > 1), the output queue will grow, causing the translation to lag further and further behind reality.
*   **Hardware Requirement:** Users without headphones will experience severe feedback/echo issues, as the system will translate its own output.

## Alternatives Considered

### 1. Maintain Half-Duplex (Status Quo)
*   *Pros:* Simple, robust, no echo issues.
*   *Cons:* Unnatural UX, unusable for long speeches.
*   *Decision:* Rejected. The project goal is high-quality S2S translation, which implies natural flow.

### 2. Dual WebSocket Connections
*   *Description:* Use one WebSocket for uploading audio and a separate WebSocket for receiving audio.
*   *Pros:* Complete separation of concerns, potentially simpler thread management.
*   *Cons:* Managing two connection states introduces synchronization issues (e.g., matching a translation to a specific input session if connections drop).
*   *Decision:* Rejected in favor of a single async WebSocket, which keeps session state consolidated and manages concurrency efficiently via Python's `asyncio`.

### 3. Server-Side Audio Queuing (Stitching)
*   *Description:* Stitch translated audio segments together on the server and stream a continuous audio stream to the client.
*   *Pros:* Client implementation is simpler (just plays a stream).
*   *Cons:* Higher latency (waiting for chunks to stitch) and difficult to handle network jitter.
*   *Decision:* Rejected. Sending discrete "Sentence Blobs" and queuing them on the client allows for lower latency and better resilience.
