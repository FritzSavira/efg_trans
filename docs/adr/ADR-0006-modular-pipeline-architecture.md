### **ADR-0006: Modular "Green-Field" Pipeline for Biblical Accuracy and Voice Cloning**

**Status:** Proposed

**Date:** 2026-02-10

#### **1. Context and Problem Statement**

The current implementation relies on `Facebook/SeamlessM4T-v2-Large`, an end-to-end (E2E) Speech-to-Speech translation model. While technically impressive for general conversation, it has critical limitations in the specific domain of **Christian church services**:

1.  **Lack of Semantic Control (Biblical Accuracy):** The model operates as a "black box." It is impossible to enforce specific theological vocabulary (e.g., ensuring "Grace" translates to "Gnade" instead of "Anmut" in specific contexts) without prohibitive fine-tuning costs.
2.  **Limited Voice Identity (Cloning):** The current E2E model transfers prosody (rhythm/intonation) but fails to capture the speaker's unique timbre (voice identity). The output sounds generic.
3.  **Local Constraints:** All processing must happen locally (Win32/Docker) without cloud dependencies due to privacy requirements, limiting the ability to use massive server-side models.

The project goal is to deliver a system that is "biblically accurate" and preserves the speaker's identity to a high degree, justifying a departure from the monolithic architecture.

#### **2. Decision**

We will transition from a monolithic E2E architecture to a **Modular "Green-Field" Pipeline (The Modular Trinity)**. This approach breaks the translation process into three specialized, state-of-the-art components running locally:

1.  **ASR (Automatic Speech Recognition):** `Faster-Whisper` (Large-v3-Turbo) for high-fidelity transcription.
2.  **LLM (Translation & Correction):** `Llama-3-8B-Instruct` (Quantized 4-bit) for context-aware translation with system prompts and glossary support.
3.  **TTS (Text-to-Speech & Cloning):** `Coqui XTTS v2` (or `StyleTTS2`) for high-quality, zero-shot voice cloning using < 6s of reference audio.

This architecture allows for explicit "intervention" at the text level (Step 2) to correct theological terms before audio synthesis.

#### **3. Key Performance Indicators (KPIs)**

The success of this architecture will be measured against five quantifiable metrics during development and in production:

| ID | Metric | Definition | Target | Measurement Method |
| :--- | :--- | :--- | :--- | :--- |
| **KPI-1** | **E2E Latency** | Time from `speech_end` (VAD) to `audio_start` (First byte). | **< 4000 ms** | System logs timestamp diff. |
| **KPI-2** | **Theological Accuracy (TTA)** | % of correct domain-specific terms in a test set of 50 liturgical sentences. | **> 95%** | Automated diff against a "Gold Standard" glossary. |
| **KPI-3** | **Speaker Similarity (SSS)** | Cosine similarity between source and target audio embeddings. | **> 0.75** | `Resemblyzer` or `WavLM` embedding comparison. |
| **KPI-4** | **Hardware Footprint** | Total VRAM usage during active translation. | **< 12 GB** | `nvidia-smi` monitoring (Target: RTX 3060/4070 class). |
| **KPI-5** | **Hallucination Rate** | Frequency of non-audio-based text generation (e.g., "Thank you for watching"). | **< 1 event/hour** | Log analysis of `prob` scores < threshold in Whisper. |

#### **4. Consequences of the Decision**

**Positive Consequences (Advantages):**
*   **Semantic Control:** The intermediate text layer allows using LLM System Prompts ("You are a theological translator...") and RAG (Glossaries) to ensure biblical accuracy.
*   **True Voice Cloning:** Specialized TTS models (XTTS) offer significantly better timbre replication than E2E prosody transfer.
*   **Modularity:** Individual components can be upgraded independently (e.g., swapping Llama-3 for Llama-4) without retraining the entire pipeline.
*   **Debuggability:** Errors can be traced to specific stages (Transcription vs. Translation vs. Synthesis).

**Negative Consequences (Disadvantages):**
*   **Increased Latency:** The sequential nature (Audio -> Text -> Text -> Audio) inherently adds latency compared to E2E. Optimization (streaming) is critical.
*   **Complexity:** Managing three distinct models and their inter-process communication increases architectural complexity.
*   **Hardware Requirements:** Running three models simultaneously requires efficient VRAM management (quantization, offloading).

#### **5. Alternatives Considered**

*   **Fine-tuning SeamlessM4T:** Rejected due to extreme hardware requirements (A100 clusters) and lack of training data.
*   **Cloud APIs (OpenAI/Google):** Rejected due to strict privacy requirements (Local-only mandate).
*   **Hybrid (Seamless + RAG):** Rejected because SeamlessM4T does not support text injection/constraints natively during generation.
