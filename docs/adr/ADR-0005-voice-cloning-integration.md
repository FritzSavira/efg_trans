### **ADR-0005: Voice Cloning Integration for Personalized Translation**

**Status:** Proposed

**Date:** 2026-02-10

#### **1. Context and Problem Statement**

The current implementation of the translation engine uses a set of static speaker IDs (e.g., ID 7 for female, ID 12 for male) provided by the SeamlessM4T v2 model. While functional, this approach has several drawbacks:
*   **Lack of Personalization:** The translated voice does not match the original speaker's vocal characteristics. In a church service context, the speaker's identity and emotional delivery are vital for the listener's experience.
*   **Prosody Loss:** Static voices often fail to capture the intonation, rhythm, and emphasis of the original speaker, leading to a more "robotic" and less engaging translation.
*   **Manual Selection:** Users must manually select a gender or voice profile, which is an extra step and may not perfectly fit the actual speaker.

We need a way to automatically adapt the output voice to the original speaker's characteristics without requiring manual intervention or pre-trained voice models.

#### **2. Decision**

We will integrate the **Zero-Shot Speaker Adaptation (Voice Cloning)** capability inherent in the **SeamlessM4T v2** model.

Specifically:
1.  **Extraction:** Instead of using a `speaker_id`, we will use the input audio segment (the source speech) to generate a **Speaker Embedding**.
2.  **Conditioning:** This embedding will be passed to the model's `generate` function using the `spkr_cond_input` (or equivalent `speaker_embedding` workflow) parameter.
3.  **Refinement (Optional):** We will implement an optional "Calibration Mode" where a few seconds of clean audio from the speaker can be recorded at the start of a session to create a high-quality, stable embedding for the entire duration of the service.

#### **3. Consequences of the Decision**

**Positive Consequences (Advantages):**
*   **Enhanced Realism:** The translated speech will sound significantly more like the original speaker, maintaining their unique vocal "fingerprint."
*   **Improved Prosody:** SeamlessM4T v2's cloning mechanism is designed to better preserve the emotional nuance and emphasis of the source speech.
*   **Zero-Shot Capability:** No prior training or fine-tuning is required; it works instantly with any new speaker.
*   **Privacy:** Since the cloning happens locally within the same model execution, no vocal data is sent to external cloud services.

**Negative Consequences (Disadvantages):**
*   **Sensitivity to Noise:** If the source audio has significant background noise or distortion, the cloned voice might inherit these artifacts or become unstable.
*   **Computational Overhead:** Generating the speaker embedding adds a very small amount of processing time (milliseconds), though this is negligible compared to the full translation cycle.
*   **Vocal Drifts:** In a fully dynamic mode, if the speaker's distance to the microphone changes, the synthesized voice might vary slightly between segments.

#### **4. Alternatives Considered**

*   **Static Speaker IDs (Status Quo):** Rejected because it fails to meet the quality and personalization requirements for church services.
*   **External TTS Services (e.g., ElevenLabs):** Rejected due to high latency, recurring costs, and privacy concerns regarding the transmission of audio to the cloud.
*   **Fine-tuned Voice Models:** Rejected because it would require hours of clean audio data and significant GPU training time for every new speaker (pastor/guest speaker), which is not feasible for live events.
