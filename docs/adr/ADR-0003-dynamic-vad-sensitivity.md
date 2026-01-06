# ADR-0003: Dynamic VAD Sensitivity Adjustment

## Status
Accepted

## Date
2026-01-05

## Context
The current implementation of the Voice Activity Detector (VAD) uses a static configuration for `min_silence_duration_ms` (defaulting to 500ms), defined in `config.yaml` at startup. This parameter dictates how long the system waits after speech stops before considering the sentence "complete" and triggering translation.

This static approach leads to poor User Experience (UX) in varying scenarios:
*   **Fast speakers** feel the system is sluggish because it waits too long after they finish speaking.
*   **Slow speakers** or those dictating thoughts are frequently interrupted by the system while pausing to think, resulting in fragmented translations.

We need a mechanism to adjust this sensitivity at runtime without restarting the server or dropping the connection.

## Decision
We will extend the existing WebSocket communication architecture to support a **Hybrid Frame Protocol** to enable real-time configuration updates.

1.  **Protocol Extension:**
    *   The WebSocket endpoint (`/ws/translate`) will no longer assume *all* incoming messages are binary audio data.
    *   It will differentiate between message types:
        *   **Binary Frames:** Treated as PCM audio chunks for the VAD processor.
        *   **Text Frames (JSON):** Treated as Control Commands (e.g., `{"type": "config", "min_silence_ms": 300}`).

2.  **Backend Implementation:**
    *   The `VADProcessor` class will expose a public method `set_min_silence(ms: int)` to update its internal state machine immediately.
    *   The WebSocket receive loop will inspect the data type of the incoming message and route it accordingly.

3.  **Frontend Implementation:**
    *   A slider control (Range Input) will be added to the UI (`200ms` - `2000ms`).
    *   On change, the frontend will serialize the configuration command to JSON and send it over the *existing* open WebSocket connection.

## Consequences

### Positive
*   **Immediate Feedback:** Users can tune the system to their speaking cadence instantly without reloading or reconnecting.
*   **Simplified State Management:** Since the configuration update happens on the same socket as the audio stream, the update is naturally applied to the correct session instance without needing complex session IDs or side-channel REST APIs.
*   **Flexibility:** Opens the door for future control commands (e.g., changing target language mid-stream, pausing VAD, etc.).

### Negative
*   **Protocol Complexity:** The backend loop must now handle distinct data types and exception handling for malformed JSON, slightly increasing the complexity of the `main.py` connection loop.
*   **Frontend Complexity:** The frontend logic must ensure it sends valid JSON structures matching the backend's expectation.

## Alternatives Considered

### 1. Reconnect with Query Parameters
*   *Description:* To change the setting, the frontend closes the WebSocket and reconnects with a new URL parameter (e.g., `ws://...?silence=200`).
*   *Pros:* Simple backend logic (config is set once at `__init__`).
*   *Cons:* Disrupts the user workflow. The user must "Stop" and "Start" to change settings.
*   *Decision:* Rejected due to poor UX.

### 2. Separate REST API Endpoint
*   *Description:* Use a `POST /config` endpoint to update settings.
*   *Pros:* Separates data plane (WebSocket) from control plane (HTTP).
*   *Cons:* High architectural complexity. The `VADProcessor` instance exists only within the scope of the WebSocket function closure. Mapping an external HTTP request to that specific in-memory instance would require a global session manager and session IDs, which is overkill for this requirement.
*   *Decision:* Rejected.

### 3. Second Control WebSocket
*   *Description:* Open two WebSockets: one for audio, one for config.
*   *Pros:* Clean separation of frame types.
*   *Cons:* Network overhead and synchronization complexity. If one socket drops, state management becomes difficult.
*   *Decision:* Rejected.
