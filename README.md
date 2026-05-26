# AWS LLM Inference — SageMaker Serverless & Amazon Bedrock

Deploy and benchmark LLMs on AWS using SageMaker Serverless Inference and Amazon Bedrock (Custom Model Import).

> 中文版請見 [README_zh.md](README_zh.md)

---

## Part 1: SageMaker Serverless Inference — distilgpt2

### Overview

| Item | Value |
|------|-------|
| Model | `distilgpt2` |
| Task | Text Generation |
| Framework | HuggingFace PyTorch 2.1.0 / Transformers 4.37.0 |
| Memory | 3072 MB |
| Max Concurrency | 5 |
| Region | `us-east-2` |

### Files

| File | Description |
|------|-------------|
| `deploy_serverless_llm.py` | Creates SageMaker Model, Endpoint Config, and Serverless Endpoint; runs cold start and warm inference tests |
| `invoke_endpoint.py` | Sends 5 concurrent requests and measures response time for each |

### Usage

#### 1. Deploy

```bash
python deploy_serverless_llm.py
```

Deployment takes approximately 5–10 minutes. A cold start test and a warm inference test are run automatically upon completion.

#### 2. Concurrent Inference

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

### Latency Reference

| State | Latency |
|-------|---------|
| Cold start (first request after idle) | ~19–21s |
| Warm inference | ~1.7–2s |

---

## Part 2: Amazon Bedrock — Llama 3.1 8B Instruct

Import a custom model from S3 into Amazon Bedrock and invoke it via API.

### Overview

| Item | Value |
|------|-------|
| Model | `meta-llama/Llama-3.1-8B-Instruct` |
| Task | Chat / Text Generation |
| Service | Amazon Bedrock (Custom Model Import) |
| Region | `us-east-2` |

### Files

| File | Description |
|------|-------------|
| `invoke_bedrock_llama.py` | Invokes the imported Llama model on Bedrock, retries every 15s up to 10 minutes, and logs cold start time and inference time to a `.txt` file |

### Setup

1. Download model from Hugging Face and upload to S3:
```bash
huggingface-cli login
python -c "
from huggingface_hub import snapshot_download
snapshot_download('meta-llama/Llama-3.1-8B-Instruct', local_dir='/tmp/llama-instruct')
"
aws s3 sync /tmp/llama-instruct s3://your-bucket/llama-3.1-8b-instruct/
```

2. Import model in Bedrock Console → Imported models → Import model
   - Source: `s3://your-bucket/llama-3.1-8b-instruct/`
   - Service role must have `s3:GetObject` and `s3:ListBucket` on the bucket

3. Update `modelId` in `invoke_bedrock_llama.py` with your imported model ARN

### Usage

```bash
python invoke_bedrock_llama.py
```

Retries every 15 seconds (up to 10 minutes) until the model is ready, then invokes it and saves results to a timestamped log file.

### Latency Reference

| State | Latency |
|-------|---------|
| Cold start (model not ready) | ~4–7 min |
| Warm inference | ~0.6–1.3s |

---

## Prerequisites

- AWS account with IAM roles for SageMaker and Bedrock
- Hugging Face account with access to Llama 3.1
- Python package: `boto3`, `huggingface_hub`

```bash
pip install boto3 huggingface_hub
```
