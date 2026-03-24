# SentinelLLM: Automated Red-Team and Guardrail Defense Framework

SentinelLLM is a research prototype designed to simulate adversarial attacks against Large Language Models (LLMs) and evaluate the effectiveness of guardrail defense mechanisms.

## Project Structure

```
sentinelllm/
├── core/
│   ├── guardrail_base.py      # Abstract Base Class
│   └── guardrail_manager.py   # Pipeline Orchestrator
├── guardrails/
│   ├── rebuff_detector.py     # Injection detection
│   ├── presidio_filter.py     # PII scanning
│   ├── nemo_guardrails.py     # Policy filtering
│   └── llama_firewall.py      # Agent safety
├── attacks/
│   └── jailbreak_prompts.json  # Benchmark dataset
├── experiments/
│   ├── runner_v2.py           # V2 Research Runner
│   └── results_v2.csv         # High-fidelity logs
├── api/
│   └── server.py              # FastAPI Backend
├── ui/
│   └── dashboard.py           # Streamlit Research Console
└── requirements.txt
```

## Features

1.  **Dynamic Attack Generator**: Uses `distilgpt2` and few-shot prompting to brainstorm novel, creative adversarial prompts.
2.  **Modular AI-Driven Guardrails**:
    -   **Rebuff Detector**: Local prompt injection classification.
    -   **Presidio Filter**: PII detection and redaction using Microsoft Presidio.
    -   **NeMo Guardrails**: Topical policy filtering for research alignment.
    -   **LlamaFirewall**: Agentic tool-use safety scanner.
3.  **Local LLM**: Uses `google/flan-t5-small` for fast, private inference on CPU.
4.  **Interactive Research Dashboard**: Real-time attack analysis and latency breakdown.

## Installation & Local Run

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the **SentinelLLM V2 Research Benchmark**:
    ```bash
    python experiments/runner_v2.py
    ```
3.  Launch the **API Research Server**:
    ```bash
    python -m uvicorn api.server:app --reload --host 127.0.0.1 --port 8000
    ```
4.  Launch the **Interactive Dashboard**:
    ```bash
    streamlit run ui/dashboard.py
    ```

## Architecture & Research Presentation

-   **Phase-Oriented Pipeline**: Guardrails act as middleware in Input, Inference, Output, and Agent phases.
-   **Zero-Shot Security Filters**: Leverages Natural Language Inference (NLI) to classify user prompts against safety labels dynamically.
-   **High-Fidelity Logging**: Tracks specific guardrail triggers, latency, and redacted content for benchmarking.

## Demo Video Instructions
1.  Open the dashboard.
2.  Show the **Attack Analytics**: Explain the ASR and Block Rate trends across Rebuff and Presidio.
3.  Show the **Logs**: Scroll through the high-fidelity V2 records.
