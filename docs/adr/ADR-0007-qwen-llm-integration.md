### **ADR-0007: Integration of Qwen2.5-7B-Instruct (Q4_K_M) as LLM**

**Status:** Proposed

**Date:** 2026-02-12

#### **1. Context and Problem Statement**

The project currently uses Meta-Llama-3-8B-Instruct as its primary translation engine. While effective, there is a desire to explore other state-of-the-art open-source models that might offer better performance, language support (especially for multilingual theological contexts), or efficiency. Qwen2.5-7B-Instruct has shown excellent benchmarks in reasoning and multilingual tasks. We need to integrate Qwen2.5-7B-Instruct (quantized to 4-bit Q4_K_M) into the pipeline to evaluate its translation quality and latency.

#### **2. Decision**

We will implement a new `QwenEngine` class in `src/core/llm/qwen_engine.py` that utilizes `llama-cpp-python` to load and run the Qwen2.5-7B-Instruct GGUF model. This engine will implement the `LLMEngine` interface. 

The prompt format will be adjusted to follow the Qwen2.5 ChatML-style template:
```
<|im_start|>system
{system_message}<|im_end|>
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
```

The system will be configured via `config.yaml` to allow switching between Llama and Qwen.

#### **3. Consequences of the Decision**

**Positive Consequences (Advantages):**
- **Multilingual Performance:** Qwen2.5 is known for superior performance in non-English languages and translation tasks compared to Llama-3 in certain benchmarks.
- **Compatibility:** Using the GGUF format and `llama-cpp-python` allows us to reuse the existing infrastructure for quantized local execution.
- **Modularity:** Adding it as a separate engine maintains the project's modular architecture.

**Negative Consequences (Disadvantages):**
- **Model Storage:** Adding another 7B model requires several gigabytes of disk space (~5GB for Q4_K_M).
- **Maintenance:** Maintaining multiple prompt templates and engine classes adds a small amount of overhead.

#### **4. Alternatives Considered**
- **Llama-3.1-8B-Instruct:** A strong contender, but Qwen2.5 often outperforms it in specific multilingual benchmarks relevant to our translation needs.
- **Mistral-Nemo-12B:** Offer better quality but has higher VRAM requirements, potentially exceeding the target hardware constraints (8GB-12GB VRAM).
- **Fine-tuning existing models:** More complex and resource-intensive than integrating a strong pre-trained model.
