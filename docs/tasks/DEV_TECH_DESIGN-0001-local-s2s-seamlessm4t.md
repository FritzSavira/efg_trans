# Technical Design: Local Speech-to-Speech Translation

This document describes the technical architecture and implementation details for the **Local Speech-to-Speech (S2S)** translation system, based on **DEV_SPEC-0001**.

---

### 1. System Architecture

The system follows a client-server architecture using **WebSockets** for real-time bidirectional audio streaming. The server is built with Python (FastAPI), acting as an orchestrator for two main AI models: **Silero VAD** (Segmentation) and **SeamlessM4T v2** (Translation).

#### 1.1 High-Level Component Diagram

```mermaid
graph TD
    Client[Browser Client] -- WebSocket (Audio Stream) --> API[FastAPI Server]
    
    subgraph "Backend (Python)"
        API -- 1. Raw Chunks --> VAD[VAD Processor (Silero)]
        VAD -- 2. Segmented Speech --> Trans[Translator Engine (SeamlessM4T)]
        Trans -- 3. Translated Audio --> API
        Device[Device Manager] -.-> VAD
        Device -.-> Trans
    end
    
    API -- 4. Audio Blob --> Client
```

#### 1.2 Data Flow (Sequence)

1.  **Init:** Client connects to `/ws/translate`. Server initializes models via `DeviceManager`.
2.  **Stream:** Client sends raw PCM audio chunks (float32, 16kHz) continuously.
3.  **Buffer:** Server accumulates chunks in the `VADProcessor` buffer.
4.  **Detect:** `VADProcessor` checks for speech activity.
5.  **Trigger:** When silence (> 500ms) follows speech:
    *   `VADProcessor` returns the full sentence buffer.
    *   Buffer is passed to `TranslatorEngine`.
6.  **Translate:** `TranslatorEngine` runs inference (German -> English).
7.  **Respond:** Server sends the translated audio (PCM/WAV) back to the client.
8.  **Play:** Client receives the blob and plays it immediately.

---

### 2. Component Specification

#### 2.1 Frontend (Client)
*   **Technology:** HTML5, JavaScript (Web Audio API).
*   **Responsibilities:**
    *   Capture microphone input.
    *   Downsample audio to 16kHz (required by models).
    *   Convert to float32 mono.
    *   Send data via WebSocket.
    *   Receive and play audio response.
*   **Key Logic:** `AudioWorkletProcessor` for non-blocking processing.

#### 2.2 Backend (Server)

**A. DeviceManager**
*   **Purpose:** Abstraction for hardware resources.
*   **Logic:**
    *   Check `torch.cuda.is_available()`.
    *   Set global device: `cuda` or `cpu`.
    *   Log device status on startup.

**B. VADProcessor**
*   **Model:** `snakers4/silero-vad` (Onnx or Torch JIT).
*   **State:** Maintains a rolling buffer of audio frames.
*   **Method:** `process(chunk: bytes) -> Optional[np.ndarray]`
    *   Returns `None` if accumulating.
    *   Returns `np.ndarray` (complete sentence) if silence detected.

**C. TranslatorEngine**
*   **Model:** `facebook/seamless-m4t-v2-large` (or `medium`).
*   **Method:** `translate(audio: np.ndarray, src="deu", tgt="eng") -> np.ndarray`
    *   Pre-process audio (resample if needed, though VAD output should be 16kHz).
    *   Run `model.generate(..., generate_speech=True)`.
    *   Post-process output (Tensor to Numpy).

**D. API Layer (FastAPI)**
*   **Endpoint:** `@app.websocket("/ws/translate")`
*   **Loop:**
    ```python
    while True:
        data = await websocket.receive_bytes()
        sentence = vad.process(data)
        if sentence:
            output_audio = translator.translate(sentence)
            await websocket.send_bytes(output_audio.tobytes())
    ```

---

### 3. Data Models & API Interface

#### 3.1 WebSocket Protocol
*   **URL:** `ws://localhost:8000/ws/translate`
*   **Client -> Server:**
    *   Binary Message: Raw PCM data (Float32, 16000Hz, Mono).
*   **Server -> Client:**
    *   Binary Message: Translated PCM data (Float32, 16000Hz, Mono) OR WAV container.
    *   *Decision:* Sending WAV headers simplifies browser playback.

#### 3.2 Configuration (config.yaml)
```yaml
app:
  host: "0.0.0.0"
  port: 8000

models:
  translation:
    variant: "facebook/seamless-m4t-v2-large" # or "medium"
    src_lang: "deu"
    tgt_lang: "eng"
  vad:
    threshold: 0.5
    min_silence_duration_ms: 500
```

---

### 4. Security & Performance

#### 4.1 Performance Optimization
*   **Model Caching:** Models are downloaded to `./models_cache` to avoid repeated downloads.
*   **FP16:** Use `torch.float16` when running on GPU to halve VRAM usage and speed up inference.
*   **Threading:** VAD is fast (CPU), but Translation is blocking. Since `generate` is compute-bound, run it in a thread pool (`run_in_executor`) if the main loop blocks too much, though with a single user, synchronous execution is acceptable for simplicity in MVP.

#### 4.2 Security
*   **Input Validation:** Max buffer size in `VADProcessor` to prevent memory overflow (DoS) if no silence is detected.
*   **CORS:** Restrict `CORSMiddleware` to allow only `localhost` origin for now.

---

### 5. Implementation Plan (Refined)

1.  **Project Setup:** `pip install torch torchaudio transformers fastapi uvicorn[standard] silero-vad numpy pyyaml`.
2.  **Core Classes:** Implement `DeviceManager`, `VADProcessor`, `TranslatorEngine` in `src/core/`.
3.  **API:** Implement `src/api/main.py`.
4.  **Frontend:** Create `static/index.html`.
5.  **Testing:** Manual verification on CPU (Win 11) then GPU.
