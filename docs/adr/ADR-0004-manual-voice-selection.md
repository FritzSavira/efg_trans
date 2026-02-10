# ADR-0004: Manual Voice Selection (Speaker Identity)

*   Status: Proposed
*   Date: 2026-02-10
*   Deciders: User
*   Technical Story: [Voice Selection Feature]

## Context and Problem Statement

The current Speech-to-Speech (S2S) system uses SeamlessM4T v2's automatic speaker identity preservation. While this works well for single-speaker scenarios, it fails to adapt correctly when multiple speakers (e.g., a female and then a male speaker) appear in the same session. The model often "sticks" to the voice characteristic of the first detected speaker.

Users need a way to:
1.  Manually override the speaker identity to ensure the output voice matches the desired gender/tone.
2.  Switch back to automatic detection if desired.

## Decision Drivers

*   User experience (UX) consistency in multi-speaker environments.
*   Reliability of the output voice.
*   Simplicity of the implementation within the existing FastAPI/WebSocket architecture.

## Considered Options

1.  **Auto-Detection Only (Current):** Rely on the model's zero-shot capability to mirror the input voice.
2.  **Manual Speaker ID Selection (Selected):** Allow the user to choose between "Auto", "Male", and "Female" by passing specific `spkr_id` values or reference embeddings to the model.
3.  **Dynamic Diarization:** Implement an automated speaker diarization step before translation to detect speaker changes automatically.

## Decision Outcome

Chosen option: **Manual Speaker ID Selection**, because it provides the most immediate and reliable fix for the user's problem with minimal architectural overhead. Dynamic diarization is technically complex and might introduce significant latency.

### Implementation Details

*   **UI:** Add a "Voice" (Stimme) dropdown to `index.html`.
*   **Protocol:** Add a `voice` parameter to the WebSocket connection string.
*   **Backend:** 
    *   Map "Male" and "Female" to representative speaker IDs supported by SeamlessM4T v2 (e.g., specific IDs from the training set or reference embeddings).
    *   Pass the selected `spkr_id` to the `model.generate` method in `TranslatorEngine`.
    *   If "Auto" is selected, no `spkr_id` is passed, maintaining existing behavior.

## Consequences

### Positive
*   Improved reliability in multi-speaker scenarios.
*   User empowerment through manual control.
*   Low latency impact.

### Negative
*   Increases UI complexity slightly.
*   Selected "Male"/"Female" IDs might not perfectly represent all users, but provide a consistent alternative to "Auto".
*   Manual switching requires user intervention.

## Pros and Cons of the Options

### Option 2: Manual Speaker ID Selection
*   Good: Fast implementation, 100% reliability for gender consistency.
*   Bad: Requires user action, static IDs might sound "generic".

### Option 3: Dynamic Diarization
*   Good: Fully automatic.
*   Bad: High latency, complex to implement, prone to errors in noisy environments.
