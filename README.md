# Modular Trinity S2S Translator

A local, privacy-preserving Speech-to-Speech translation system optimized for theological contexts (church services) with authentic voice cloning and low-latency performance monitoring.

## 🚀 Features

- **Modular Pipeline:** Independent ASR (Whisper), LLM (Qwen/Llama), and TTS (XTTS) stages.
- **Voice Cloning:** Clone the original speaker's voice using a short (~6s) audio reference.
- **Theological Accuracy:** Optimized LLM prompting for biblical and church-specific terminology.
- **Performance Dashboard:** Real-time monitoring of ASR, LLM, TTS, and End-to-End latency.
- **Session Analytics:** Detailed JSONL logs for every translation session for offline analysis.
- **Privacy First:** 100% local execution via Docker and NVIDIA GPU.

## 🛠 Prerequisites

- **OS:** Windows (WSL2 recommended) or Linux.
- **Hardware:** NVIDIA GPU with at least 12GB VRAM.
- **Software:** Docker, Docker Compose, NVIDIA Container Toolkit.

## 📥 Setup

1.  **Download Models:**
    Ensure you have the following models in the `models/` folder:
    - Qwen2.5-7B-Instruct (GGUF format).
    - Whisper `large-v3` weights.
    - XTTS v2 weights (handled automatically by the engine usually).

2.  **Configuration:**
    Edit `config.yaml` to set your model paths and preferences.

3.  **Start the System:**
    ```bash
    docker-compose build
    docker-compose up -d
    ```

4.  **Access the UI:**
    Open `http://localhost:8000` in your browser.

## 🖥 Usage

1.  **Calibration:** Upload a 6-10 second WAV file of the person who will be speaking (e.g., the Pastor).
2.  **Language Selection:** Choose the source and target languages.
3.  **Start:** Click "Start Translation" and speak into the microphone, or use "Stream File" to process an existing recording.
4.  **Monitor:** Watch the Performance Dashboard to ensure End-to-End latency stays below the 4000ms KPI target.

## 📊 Analytics

Performance logs are stored in `logs/sessions/`. These files use the `.jsonl` format and contain detailed metrics for every sentence processed, including the Real-Time Factor (RTF).

## 📄 Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Development Guidelines](docs/DEVELOPMENT_GUIDELINES.md)
- [ADR Index](docs/adr/)
