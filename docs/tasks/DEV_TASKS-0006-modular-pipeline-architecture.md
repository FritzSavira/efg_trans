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

- [ ] **Step 1.1: Archive Legacy Code**
    - [ ] **Action:** Create a directory `src_legacy/`.
    - [ ] **Action:** Move the existing `src/` folder content into `src_legacy/`.
    - [ ] **Action:** Create a fresh, empty `src/` directory.
    - [ ] **Action:** Create an `__init__.py` file in `src/`.
    - [ ] **Verification:** Run `ls -R` (or similar) to confirm `src/` is empty (except init) and `src_legacy/` contains the old code.

- [ ] **Step 1.2: Establish New Directory Structure**
    - [ ] **Action:** Create the following subdirectories inside `src/`:
        - `src/core/asr`
        - `src/core/llm`
        - `src/core/tts`
        - `src/core/audio`
        - `src/pipeline`
        - `src/api`
    - [ ] **Action:** Add an empty `__init__.py` to each of these new directories.
    - [ ] **Verification:** Verify the tree structure exists.

- [ ] **Step 1.3: Update Dependencies**
    - [ ] **Action:** Update `requirements.txt`. Add:
        - `faster-whisper==0.10.0`
        - `llama-cpp-python>=0.2.26`
        - `TTS>=0.22.0` (Coqui)
        - `sounddevice`
        - `numpy`
        - `torch`
    - [ ] **Action:** Run `pip install -r requirements.txt` (This may take time).
    - [ ] **Verification:** Run `python -c "import faster_whisper; import llama_cpp; import TTS; print('Imports successful')"` to ensure libraries are installed correctly.

- [ ] **Step 1.4: Define Interfaces**
    - [ ] **Action:** Create `src/core/interfaces.py`.
    - [ ] **Action:** Define the abstract base classes `ASREngine`, `LLMEngine`, and `TTSEngine` exactly as specified in `DEV_TECH_DESIGN-0006` (Section 4.1).
    - [ ] **Action:** Define the data classes `AudioSegment`, `TranscriptionResult`, `TranslationResult` using `@dataclass`.
    - [ ] **Verification:** Run `ruff check src/core/interfaces.py` to ensure syntax and style are correct.

---

## Phase 2: Core Components Implementation (The Trinity)

*Goal: Implement the three engines in isolation to ensure each works correctly before linking them.*

- [ ] **Step 2.1: Implement ASR Engine (Whisper)**
    - [ ] **Action:** Create `src/core/asr/whisper_engine.py`.
    - [ ] **Action:** Implement `WhisperASR` class inheriting from `ASREngine`.
    - [ ] **Action:** In `__init__`, load `faster_whisper.WhisperModel("large-v3-turbo", device="cuda", compute_type="float16")`.
    - [ ] **Action:** Implement `transcribe(audio_np)` method.
    - [ ] **Verification (Interactive Test):**
        1.  Create a temporary script `test_asr_manual.py`.
        2.  Load a short WAV file (e.g., record one with your mic).
        3.  Instantiate `WhisperASR` and call `transcribe`.
        4.  Print the text.
        5.  **Expected Result:** The printed text matches the spoken audio.

- [ ] **Step 2.2: Implement LLM Engine (Llama-3)**
    - [ ] **Action:** Create `src/core/llm/llama_engine.py`.
    - [ ] **Action:** Implement `LlamaTranslator` class inheriting from `LLMEngine`.
    - [ ] **Action:** In `__init__`, load `Llama` from `llama_cpp`. Ensure `n_gpu_layers=-1` for full GPU offload.
    - [ ] **Action:** Implement `translate(text, src, tgt)` method. Construct the prompt: `System: You are a translator. User: Translate: {text}`.
    - [ ] **Verification (Interactive Test):**
        1.  Create `test_llm_manual.py`.
        2.  Instantiate `LlamaTranslator`.
        3.  Call `translate("The grace of God.", "en", "de")`.
        4.  **Expected Result:** Output should be "Die Gnade Gottes." (Check for theology correctness).

- [ ] **Step 2.3: Implement TTS Engine (XTTS)**
    - [ ] **Action:** Create `src/core/tts/xtts_engine.py`.
    - [ ] **Action:** Implement `XTTSEngineWrapper` class inheriting from `TTSEngine`.
    - [ ] **Action:** In `__init__`, load `TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cuda")`.
    - [ ] **Action:** Implement `synthesize(text, speaker_wav)` method.
    - [ ] **Verification (Interactive Test):**
        1.  Create `test_tts_manual.py`.
        2.  Record a 5s sample of your own voice as `ref.wav`.
        3.  Instantiate `XTTSEngineWrapper`.
        4.  Call `synthesize("Hello, this is a voice cloning test.", "ref.wav")`.
        5.  Play the result.
        6.  **Expected Result:** The audio should sound like you.

---

## Phase 3: Pipeline Integration & Orchestration

*Goal: Connect the components using async queues to enable streaming translation.*

- [ ] **Step 3.1: Create Orchestrator**
    - [ ] **Action:** Create `src/pipeline/orchestrator.py`.
    - [ ] **Action:** Define `PipelineOrchestrator` class.
    - [ ] **Action:** Initialize the 3 engines and 3 `asyncio.Queue`s (`audio_q`, `text_q`, `speech_q`).
    - [ ] **Action:** Implement `start()` method that launches 3 worker tasks (ASR-Worker, LLM-Worker, TTS-Worker).

- [ ] **Step 3.2: Implement VAD & Input Handling**
    - [ ] **Action:** Port the VAD logic from `src_legacy` (or use `silero-vad`) into `src/core/audio/vad.py`.
    - [ ] **Action:** Update `orchestrator.py` to accept raw bytes, run VAD, and push to `audio_q` only when a sentence is complete.

- [ ] **Step 3.3: Connect the Workers**
    - [ ] **Action:** Implement `asr_worker()`: Pull audio -> Transcribe -> Push text.
    - [ ] **Action:** Implement `llm_worker()`: Pull text -> Translate -> Push translation.
    - [ ] **Action:** Implement `tts_worker()`: Pull translation -> Synthesize -> Push audio bytes.
    - [ ] **Verification:** Create an integration test `tests/test_pipeline_local.py` that feeds a mock audio file into the orchestrator and asserts that audio comes out the other end.

---

## Phase 4: Frontend Re-Integration

*Goal: Update the WebSocket API and HTML frontend to work with the new pipeline.*

- [ ] **Step 4.1: Update WebSocket API**
    - [ ] **Action:** Update `src/api/main.py`.
    - [ ] **Action:** Remove old `TranslatorEngine` references.
    - [ ] **Action:** Instantiate `PipelineOrchestrator`.
    - [ ] **Action:** Update the WebSocket loop to feed `orchestrator.process_audio(bytes)` and await `orchestrator.get_output()`.

- [ ] **Step 4.2: Update Frontend UI for Cloning**
    - [ ] **Action:** Modify `static/index.html`.
    - [ ] **Action:** Add a "Reference Audio" file input (separate from the main translation input).
    - [ ] **Action:** Send this reference audio as a special "Configuration" message to the backend to set the target voice.

- [ ] **Step 4.3: Final System Test**
    - [ ] **Action:** Start the server.
    - [ ] **Action:** Upload a reference voice.
    - [ ] **Action:** Speak into the microphone.
    - [ ] **Verification:**
        1.  Latency check (is it < 4s?).
        2.  Voice check (does it sound like the reference?).
        3.  Translation check (is it accurate?).

---

## Phase 5: Optimization & Cleanup

- [ ] **Step 5.1: Clean Code Check**
    - [ ] **Action:** Run `black .`.
    - [ ] **Action:** Run `ruff check .`.
    - [ ] **Action:** Fix any linting errors.

- [ ] **Step 5.2: Documentation**
    - [ ] **Action:** Update `README.md` with new installation instructions (the 3 models).
    - [ ] **Action:** Document the new architecture briefly in `docs/ARCHITECTURE.md` (create if missing).
