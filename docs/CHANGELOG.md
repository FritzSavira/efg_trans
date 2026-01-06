# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-01-06
### Added
- **Dynamic VAD Sensitivity:** Added a UI slider to adjust the `min_silence_duration_ms` at runtime. The backend now supports a hybrid WebSocket protocol (Binary for Audio, JSON for Config).
- **Continuous Duplex Pipeline:** Implemented asynchronous producer-consumer architecture in `src/api/main.py`. This allows the user to speak continuously while the system translates and plays back previous sentences in parallel (Reference: `ADR-0002`).
- **Frontend Audio Queue:** Added `AudioQueue` class in `static/index.html` to manage sequential playback of translated audio segments, preventing overlap.
- **VAD Padding:** Added configurable silence padding (`padding_ms`) in `src/core/vad_processor.py` to prevent audio clipping at the start/end of detected sentences.
- **Headphone Warning:** Added a UI alert in `index.html` advising users to use headphones to avoid echo loops in continuous mode.
- **Config Documentation:** Added detailed English comments to `config.yaml` to explain all parameters.

### Changed
- Refactored `websocket_endpoint` to use `asyncio.Queue` and `asyncio.gather`.
- Decoupled `input_loop` (VAD) and `translation_loop` (Inference).
- Running translation inference in a separate thread using `run_in_executor` to avoid blocking the event loop.

## [1.0.0] - 2026-01-05

### Added
- **Core Infrastructure:**
    - Established project skeleton and directory structure (`src/core`, `src/api`, `static`).
    - Added `requirements.txt` with core dependencies (FastAPI, PyTorch, Silero VAD, SeamlessM4T).
    - Added `pyproject.toml` for tool configuration and Pytest resolution.
    - Implemented `DeviceManager` for automatic CPU/CUDA hardware detection (ADR-0001).
    - Implemented `config.yaml` and `src/core/config.py` for centralized configuration.

- **AI Components:**
    - Implemented `VADProcessor` using `silero-vad` with robust `VADIterator` logic for sentence segmentation.
    - Implemented `TranslatorEngine` integrating Meta's `seamless-m4t-v2-large` model for Speech-to-Speech translation.
    - Added support for NVIDIA GPU (CUDA) acceleration with FP16 precision.

- **Frontend:**
    - Developed a modern HTML/JS interface with manual 16kHz downsampling to ensure compatibility across different browser/hardware environments.
    - Implemented automatic WAV playback using the Web Audio API.

- **Docker Support:**
    - Created `Dockerfile` and `docker-compose.yaml` with NVIDIA GPU resource reservation.
    - Implemented model caching via volume mounts to persist large model downloads.

- **Debugging & Reliability:**
    - Added "Flight Recorder" logging: Input and Output audio are automatically saved to `static/debug/` for analysis.
    - Implemented output normalization to prevent audio clipping.

### Fixed
- Fixed module resolution issue in tests by adding `pyproject.toml`.
- Fixed VAD chunk size issue by implementing a rolling buffer and windowing logic.
- Resolved audio latency and "hallucination" issues by upgrading to `SeamlessM4Tv2Model`.
- Fixed sample rate mismatch between browser and backend via manual JS downsampling.
- Fixed `soundfile` compatibility issue by casting `float16` to `float32` before WAV export.
- Fixed WebSocket routing conflict by isolating `StaticFiles` mounting and using explicit `FileResponse` for the root path.

### Docs
- Created `ADR-0001` (S2S Architecture).
- Created `DEV_SPEC-0001`, `DEV_TECH_DESIGN-0001`, and `DEV_TASKS-0001`.
- Added `DEVELOPMENT_GUIDELINES.md` and `CODING_STYLE.md`.