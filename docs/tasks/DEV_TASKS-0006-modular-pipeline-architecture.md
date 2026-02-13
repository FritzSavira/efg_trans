# DEV_TASKS-0006: Modular "Green-Field" Pipeline (The Modular Trinity)

This task plan guides the transition from the legacy monolithic architecture to the new modular pipeline (Whisper + Llama + XTTS), as defined in **ADR-0006** and **DEV_TECH_DESIGN-0006**.

**Developer:** Please follow these steps precisely. The plan is broken into phases and small steps to allow for interruptions and ensure stability. After each "Verification" step, report the outcome. This iterative process is crucial for maintaining quality.

**Briefing Documents:**
*   [ADR-0006: Modular Pipeline Architecture](../../docs/adr/ADR-0006-modular-pipeline-architecture.md)
*   [DEV_SPEC-0006: Modular Pipeline Specification](../../docs/tasks/DEV_SPEC-0006-modular-pipeline-architecture.md)
*   [DEV_TECH_DESIGN-0006: Technical Design](../../docs/tasks/DEV_TECH_DESIGN-0006-modular-pipeline-architecture.md)

---

## Phase 1: Preparation & "Green-Field" Setup

*Goal: Archive the old codebase to prevent confusion and establish the new directory structure with correct dependencies.*

- [x] **Step 1.1: Archive Legacy Code**
    - [x] **Action:** Create a directory `src_legacy/`.
    - [x] **Action:** Move the existing `src/` folder content into `src_legacy/`.
    - [x] **Action:** Create a fresh, empty `src/` directory.
    - [x] **Action:** Create an `__init__.py` file in `src/`.
    - [x] **Verification:** Run `ls -R` (or similar) to confirm `src/` is empty (except init) and `src_legacy/` contains the old code.

- [x] **Step 1.2: Establish New Directory Structure**
    - [x] **Action:** Create the following subdirectories inside `src/`:
        - `src/core/asr`
        - `src/core/llm`
        - `src/core/tts`
        - `src/core/audio`
        - `src/pipeline`
        - `src/api`
    - [x] **Action:** Add an empty `__init__.py` to each of these new directories.
    - [x] **Verification:** Verify the tree structure exists.

- [x] **Step 1.3: Update Dependencies**
    - [x] **Action:** Update `requirements.txt`. Add:
        - `faster-whisper==0.10.0`
        - `llama-cpp-python>=0.2.26`
        - `TTS>=0.22.0` (Coqui)
        - `sounddevice`
        - `numpy`
        - `torch`
    - [x] **Action:** Run `pip install -r requirements.txt` (This may take time).
    - [x] **Verification:** Run `python -c "import faster_whisper; import llama_cpp; import TTS; print('Imports successful')"` to ensure libraries are installed correctly.

- [x] **Step 1.4: Define Interfaces**
    - [x] **Action:** Create `src/core/interfaces.py`.
    - [x] **Action:** Define the abstract base classes `ASREngine`, `LLMEngine`, and `TTSEngine` exactly as specified in `DEV_TECH_DESIGN-0006` (Section 4.1).
    - [x] **Action:** Define the data classes `AudioSegment`, `TranscriptionResult`, `TranslationResult` using `@dataclass`.
    - [x] **Verification:** Run `ruff check src/core/interfaces.py` to ensure syntax and style are correct.

---

## Phase 2: Core Components Implementation (The Trinity)

*Goal: Implement the three engines in isolation to ensure each works correctly before linking them.*

- [x] **Step 2.1: Implement ASR Engine (Whisper)**
    - [x] **Action:** Create `src/core/asr/whisper_engine.py`.
    - [x] **Action:** Implement `WhisperASR` class inheriting from `ASREngine`.
    - [x] **Action:** In `__init__`, load `faster_whisper.WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")`.
    - [x] **Action:** Implement `transcribe(audio_np)` method.
    - [x] **Verification (Interactive Test):** Done.

- [x] **Step 2.2: Implement LLM Engine (Llama-3 / Qwen)**
    - [x] **Action:** Create `src/core/llm/llama_engine.py` and `src/core/llm/qwen_engine.py`.
    - [x] **Action:** Implement engines inheriting from `LLMEngine`.
    - [x] **Action:** In `__init__`, load model from `llama_cpp`. Ensure `n_gpu_layers=-1` for full GPU offload.
    - [x] **Action:** Implement `translate(text, src, tgt)` method.
    - [x] **Verification (Interactive Test):** Done.

- [x] **Step 2.3: Implement TTS Engine (XTTS)**
    - [x] **Action:** Create `src/core/tts/xtts_engine.py`.
    - [x] **Action:** Implement `XTTSEngineWrapper` class inheriting from `TTSEngine`.
    - [x] **Action:** In `__init__`, load `TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")`.
    - [x] **Action:** Implement `synthesize(text, speaker_wav)` method.
    - [x] **Verification (Interactive Test):** Done.

---

## Phase 3: Pipeline Integration & Orchestration

*Goal: Connect the components using async queues to enable streaming translation.*

- [x] **Step 3.1: Create Orchestrator**
    - [x] **Action:** Create `src/pipeline/orchestrator.py`.
    - [x] **Action:** Define `PipelineOrchestrator` class.
    - [x] **Action:** Initialize the 3 engines and 3 `asyncio.Queue`s (`audio_q`, `text_q`, `speech_q`).
    - [x] **Action:** Implement `start()` method that launches 3 worker tasks (ASR-Worker, LLM-Worker, TTS-Worker).

- [x] **Step 3.2: Implement VAD & Input Handling**
    - [x] **Action:** Port the VAD logic from `src_legacy` (or use `silero-vad`) into `src/core/audio/vad.py`.
    - [x] **Action:** Update `orchestrator.py` to accept raw bytes, run VAD, and push to `audio_q` only when a sentence is complete.

- [x] **Step 3.3: Connect the Workers**
    - [x] **Action:** Implement `asr_worker()`: Pull audio -> Transcribe -> Push text.
    - [x] **Action:** Implement `llm_worker()`: Pull text -> Translate -> Push translation.
    - [x] **Action:** Implement `tts_worker()`: Pull translation -> Synthesize -> Push audio bytes.
    - [x] **Verification:** Integration verified via manual tests.

---

## Phase 4: Frontend Re-Integration

*Goal: Update the WebSocket API and HTML frontend to work with the new pipeline.*

- [x] **Step 4.1: Update WebSocket API**
    - [x] **Action:** Update `src/api/main.py`.
    - [x] **Action:** Remove old `TranslatorEngine` references.
    - [x] **Action:** Instantiate `PipelineOrchestrator`.
    - [x] **Action:** Update the WebSocket loop to feed `orchestrator.process_audio(bytes)` and await `orchestrator.get_output()`.

- [x] **Step 4.2: Update Frontend UI for Cloning**
    - [x] **Action:** Modify `static/index.html`.
    - [x] **Action:** Add a "Reference Audio" file input (separate from the main translation input).
    - [x] **Action:** Send this reference audio as a special "Configuration" message to the backend to set the target voice.

- [x] **Step 4.3: Implement Performance Dashboard**
    - [x] **Action:** Update Orchestrator to track latency per stage.
    - [x] **Action:** Send metrics via WebSocket.
    - [x] **Action:** Add dashboard UI to `static/index.html`.
    - [x] **Verification:** Metrics are visible in UI during translation.

- [x] **Step 4.4: Final System Test**
    - [x] **Action:** Start the server.
    - [x] **Action:** Upload a reference voice.
    - [x] **Action:** Speak into the microphone.
    - [x] **Verification:** Verified by user (Metrics visible, logs written).

---

## Phase 5: Optimization & Cleanup

- [x] **Step 5.1: Clean Code Check**
    - [x] **Action:** Run `black .`.
    - [x] **Action:** Run `ruff check .`.
    - [x] **Action:** Fix any linting errors.

- [x] **Step 5.2: Documentation**
    - [x] **Action:** Update `README.md` with new installation instructions (the 3 models).
    - [x] **Action:** Document the new architecture briefly in `docs/ARCHITECTURE.md` (create if missing).
