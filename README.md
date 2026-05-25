# SageMaker Serverless Inference — distilgpt2

Deploy and benchmark a Hugging Face LLM (`distilgpt2`) on AWS SageMaker Serverless Inference.

> 中文版請見 [README_zh.md](README_zh.md)

## Overview

| Item | Value |
|------|-------|
| Model | `distilgpt2` |
| Task | Text Generation |
| Framework | HuggingFace PyTorch 2.1.0 / Transformers 4.37.0 |
| Memory | 3072 MB |
| Max Concurrency | 5 |
| Region | `us-east-2` |

## Files

| File | Description |
|------|-------------|
| `deploy_serverless_llm.py` | Creates SageMaker Model, Endpoint Config, and Serverless Endpoint; runs cold start and warm inference tests |
| `invoke_endpoint.py` | Sends 5 concurrent requests and measures response time for each |

## Usage

### 1. Deploy

```bash
python deploy_serverless_llm.py
```

Deployment takes approximately 5–10 minutes. A cold start test and a warm inference test are run automatically upon completion.

### 2. Concurrent Inference

```bash
python invoke_endpoint.py
```

Sends 5 prompts concurrently and prints each response time in completion order. Results are automatically saved to a timestamped `.txt` file.

```
Sending 5 concurrent requests...

[2] 1.65s | Machine learning helps us ...
[1] 1.73s | The future of AI is ...
[3] 1.84s | Cloud computing enables ...
[5] 1.88s | Natural language processing allows ...
[4] 20.12s | Deep learning models can ...

Total wall time (slowest): 20.58s
```

Large time differences indicate a cold start on a new container. With MaxConcurrency=5, sending 5 simultaneous requests may trigger new container launches for some requests.

## Latency Reference

| State | Latency |
|-------|---------|
| Cold start (first request after idle) | ~19–21s |
| Warm inference | ~1.7–2s |

Serverless endpoints scale to zero after ~5 minutes of inactivity. The next request will trigger a cold start.

## Prerequisites

- AWS account with an IAM Role that has SageMaker execution permissions
- Python package: `boto3`

```bash
pip install boto3
```
