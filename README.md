# SageMaker Serverless Inference

Deploy a Hugging Face LLM (`distilgpt2`) on AWS SageMaker Serverless Inference.

## Overview

| Item | Value |
|------|-------|
| Model | `distilgpt2` (~300MB) |
| Task | Text Generation |
| Memory | 2048 MB |
| Max Concurrency | 5 |
| Region | `us-east-2` |

## Cold Start vs Warm Inference

| State | Latency |
|-------|---------|
| Cold start (after idle) | ~6.5s |
| Warm inference | ~1.7s |

Serverless endpoints scale to zero after ~5 minutes of inactivity, triggering a cold start on the next request.

## Files

- `deploy_serverless_llm.py` — Creates the SageMaker model, endpoint config, and serverless endpoint
- `invoke_endpoint.py` — Invokes the endpoint and measures response time

## Usage

### Deploy

```bash
python deploy_serverless_llm.py
```

### Invoke

```bash
python invoke_endpoint.py
```

Or invoke directly with boto3:

```python
import boto3, json

runtime = boto3.client("sagemaker-runtime", region_name="us-east-2")

response = runtime.invoke_endpoint(
    EndpointName="distilgpt2-serverless",
    ContentType="application/json",
    Body=json.dumps({"inputs": "The future of AI is"}),
)
print(json.loads(response["Body"].read()))
```

## Prerequisites

- AWS credentials with SageMaker permissions
- Python packages: `boto3`
