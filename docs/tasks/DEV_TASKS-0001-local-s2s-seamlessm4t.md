# DEV_TASKS-0001: Local Speech-to-Speech Translation (with Docker)

This task plan implements the local Speech-to-Speech (S2S) translation system using SeamlessM4T and Silero VAD, as defined in **ADR-0001**. It concludes with a full Dockerization of the application.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome. This iterative process is crucial for maintaining quality.

**Briefing Documents:**
*   [ADR-0001: Local S2S using SeamlessM4T](../../docs/adr/ADR-0001-local-s2s-seamlessm4t.md)
*   [DEV_SPEC-0001: Requirements Specification](../../docs/tasks/DEV_SPEC-0001-local-s2s-seamlessm4t.md)
*   [DEV_TECH_DESIGN-0001: Technical Design](../../docs/tasks/DEV_TECH_DESIGN-0001-local-s2s-seamlessm4t.md)

---

## Phase 1: Project Initialization & Infrastructure

*Goal: Setup the Python environment, install dependencies, and establish the core configuration loading mechanism.*

- [x] **Step 1.1: Project Skeleton & Dependencies**
    - [x] **Action:** Create the directory structure:
        - `src/core`
        - `src/api`
        - `static`
        - `tests`
        - `models_cache` (add to `.gitignore`)
    - [x] **Action:** Create `requirements.txt` containing:
        - `fastapi`
        - `uvicorn[standard]`
        - `torch`
        - `torchaudio`
        - `transformers`
        - `silero-vad`
        - `numpy`
        - `pyyaml`
        - `pytest`
        - `httpx` (for testing)
        - `black`
        - `ruff`
    - [x] **Action:** Install dependencies in the virtual environment.
    - [x] **Verification:** Run `python -c "import torch; import transformers; print('Setup OK')"` and confirm output.

- [x] **Step 1.2: Configuration System**
    - [x] **Action:** Create `config.yaml` in the root directory with the structure defined in `DEV_TECH_DESIGN-0001` (Section 3.2).
    - [x] **Action:** Implement `src/core/config.py` to load this YAML file into a Python dictionary.
    - [x] **Verification (Interactive Test):**
        1.  Create a temporary script `test_config.py` that imports the config loader and prints `app.port`.
        2.  Run the script.
        3.  **Expected Result:** It prints `8000`.

- [x] **Step 1.3: Device Manager (Hardware Abstraction)**
    - [x] **Action:** Create `src/core/device_manager.py`.
    - [x] **Action:** Implement `class DeviceManager` with a method `get_device()` that returns `cuda` if available, else `cpu`.
    - [x] **Action:** Add logging in `__init__` to state which device was found.
    - [x] **Verification (Interactive Test):**
        1.  Create a temporary script `test_device.py`.
        2.  Instantiate `DeviceManager`.
        3.  Run it.
        4.  **Expected Result:** It logs "Running on CPU" (or "Running on CUDA:0" if configured).

---

## Phase 2: Core AI Components (Backend)

*Goal: Implement the VAD (Segmentation) and Translation Engine independently before connecting them to the API.*

- [x] **Step 2.1: VAD Processor**
    - [x] **Action:** Create `src/core/vad_processor.py`.
    - [x] **Action:** Implement `class VADProcessor`.
        - Load `snakers4/silero-vad` in `__init__`.
        - Implement `process(chunk: bytes) -> Optional[np.ndarray]`.
        - Logic: Append chunk to buffer. Use model to detect probability. If silence > threshold for > min_duration, return buffered audio.
    - [x] **Verification (Interactive Test):**
        1.  Create a unit test `tests/test_vad.py`.
        2.  Generate synthetic silence (numpy zeros) and pass it to `process`.
        3.  Run `pytest tests/test_vad.py`.
        4.  **Expected Result:** Tests pass (silence detection logic works).

- [x] **Step 2.2: Translator Engine (The Heavy Lifter)**
    - [x] **Action:** Create `src/core/translator_engine.py`.
    - [x] **Action:** Implement `class TranslatorEngine`.
        - In `__init__`, load `facebook/seamless-m4t-v2-large` (or `medium` via config) using `transformers.AutoProcessor` and `SeamlessM4TModel`.
        - Use `DeviceManager` to move model to CPU/GPU.
        - Implement `translate(audio: np.ndarray) -> np.ndarray`.
    - [x] **Action:** Ensure `generate_speech=True` is used in the model call.
    - [x] **Verification (Interactive Test):**
        1.  Create a script `test_translate.py`.
        2.  Load a small dummy audio file (or generate a sine wave).
        3.  Pass it to `translate`.
        4.  Save output to `test_output.wav`.
        5.  **Expected Result:** Script finishes without OOM. Output file exists. (Result: 53.83s on CPU)

---

## Phase 3: API & WebSocket Layer

*Goal: Connect the components via FastAPI and WebSockets.*

- [x] **Step 3.1: FastAPI Setup & HTTP Routes**
    - [x] **Action:** Create `src/api/main.py`.
    - [x] **Action:** Initialize `FastAPI` app.
    - [x] **Action:** Add `CORSMiddleware`.
    - [x] **Action:** Add a root endpoint `GET /` returning `{"status": "online"}`.
    - [x] **Verification:** Run `uvicorn src.api.main:app --reload` and visit `http://localhost:8000`.

- [x] **Step 3.2: WebSocket Orchestrator**
    - [x] **Action:** In `src/api/main.py`, create `@app.websocket("/ws/translate")`.
    - [x] **Action:** Instantiate `VADProcessor` and `TranslatorEngine` (Warning: Model loading is slow. Consider loading them on app startup `lifespan` event).
    - [x] **Action:** Implement the loop: Receive Bytes -> VAD -> (if sentence) -> Translate -> Send Bytes.
    - [x] **Verification:** Use a Python script `tests/test_ws_client.py` to connect and send bytes. Ensure connection is stable.

---

## Phase 4: Frontend & Integration

*Goal: Browser-based microphone input and audio playback.*

- [x] **Step 4.1: Static Files Setup**
    - [x] **Action:** Configure FastAPI to serve static files from `/static`.
    - [x] **Action:** Create `static/index.html`.
    - [x] **Action:** Add basic UI: "Start Recording" button, "Status" div.

- [x] **Step 4.2: Audio Capture (JS)**
    - [x] **Action:** In `static/index.html`, implement `navigator.mediaDevices.getUserMedia`.
    - [x] **Action:** Implement Audio Resampling to 16kHz (Web Audio API).
    - [x] **Action:** Send `Float32Array` chunks to WebSocket.

- [x] **Step 4.3: Audio Playback (JS)**
    - [x] **Action:** Handle `ws.onmessage`.
    - [x] **Action:** Queue received audio blobs.
    - [x] **Action:** Play them sequentially using `AudioContext`.
    - [x] **Verification (Interactive Test):**
        1.  Open `http://localhost:8000`.
        2.  Click Start.
        3.  Speak "Hallo".
        4.  **Expected Result:** Hear "Hello" (English) back from speakers.

---

## Phase 5: Cleanup & Polish

*Goal: Ensure code quality and robust error handling.*

- [x] **Step 5.1: Error Handling**
    - [x] **Action:** Add try/except blocks in the WebSocket loop to handle disconnection.
    - [x] **Action:** Handle `RuntimeError` during inference.

- [x] **Step 5.2: Code Quality Check**
    - [x] **Action:** Run `black .`
    - [x] **Action:** Run `ruff check .`
    - [x] **Action:** Fix any issues.

---

## Phase 6: Containerization (Docker)

*Goal: Package the application for portable execution with GPU support.*

- [x] **Step 6.1: Prepare Docker Context**
    - [x] **Action:** Create `.dockerignore`.
        - Add `models_cache/` (we will mount this, not copy it, to keep build small).
        - Add `.git/`, `__pycache__/`, `venv/`.
    - [x] **Action:** Verify `requirements.txt` is up to date and pinned.

- [x] **Step 6.2: Dockerfile**
    - [x] **Action:** Create `Dockerfile`.
    - [x] **Base Image:** Use `python:3.10-slim`.
    - [x] **System Deps:** Run `apt-get install -y ffmpeg libsndfile1`.
    - [x] **Python Deps:** `COPY requirements.txt .` and `RUN pip install ...`.
    - [x] **Source:** `COPY . /app`.
    - [x] **Command:** `CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]`.

- [x] **Step 6.3: Docker Compose with GPU Support**
    - [x] **Action:** Create `docker-compose.yaml`.
    - [x] **Service:** `s2s-app`.
    - [x] **Volumes:** Mount `./models_cache` to `/app/models_cache` (Persist downloaded models).
    - [x] **Ports:** Map `8000:8000`.
    - [x] **Deploy Config:** Add `resources` section to enable NVIDIA GPU access (NVIDIA Container Toolkit must be installed on host).
    - [x] **Verification (Interactive Test):**
        1.  Run `docker-compose up --build`.
        2.  Observe logs. Is it downloading models? (First run only).
        3.  Observe logs. Does it say "Running on CUDA"? (If GPU available).
        4.  Access `http://localhost:8000` from the browser and test translation.