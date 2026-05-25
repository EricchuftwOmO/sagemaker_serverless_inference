# SageMaker Serverless Inference — distilgpt2

Deploy and benchmark a Hugging Face LLM (`distilgpt2`) on AWS SageMaker Serverless Inference.

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
| `deploy_serverless_llm.py` | 建立 SageMaker Model、Endpoint Config、Serverless Endpoint，並測試冷啟動與暖機推論 |
| `invoke_endpoint.py` | 同時送出 5 個請求，分別計時每個推論的回應時間 |

## Usage

### 1. Deploy

```bash
python deploy_serverless_llm.py
```

部署約需 5–10 分鐘。完成後會自動執行一次冷啟動測試和一次暖機測試。

### 2. Concurrent Inference

```bash
python invoke_endpoint.py
```

同時送出 5 個 prompt，輸出每個請求的回應時間（按完成順序印出）：

```
同時送出 5 個請求...

[2] 1.65s | Machine learning helps us ...
[1] 1.73s | The future of AI is ...
[3] 1.84s | Cloud computing enables ...
[5] 1.88s | Natural language processing allows ...
[4] 20.12s | Deep learning models can ...

總等待時間（最慢那個）: 20.58s
```

時間差異大的請求代表觸發了新 container 的冷啟動（Max Concurrency = 5，同時打滿時部分請求可能需要等待新 container 啟動）。

## Latency Reference

| 狀態 | 延遲 |
|------|------|
| 冷啟動（idle 後第一次） | ~19–21s |
| 暖機推論 | ~1.7–2s |

Serverless endpoint 閒置約 5 分鐘後會縮減至零，下次請求會觸發冷啟動。

## Prerequisites

- AWS 帳號，IAM Role 需有 SageMaker 執行權限
- Python 套件：`boto3`

```bash
pip install boto3
```
