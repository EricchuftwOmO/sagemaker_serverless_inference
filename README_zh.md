# AWS LLM 推論 — SageMaker Serverless & Amazon Bedrock

使用 AWS SageMaker Serverless Inference 和 Amazon Bedrock（自訂模型匯入）部署並測試 LLM。

> For English version, see [README.md](README.md)

---

## Part 1: SageMaker Serverless Inference — distilgpt2

### 概覽

| 項目 | 值 |
|------|-----|
| 模型 | `distilgpt2` |
| 任務 | 文字生成 |
| 框架 | HuggingFace PyTorch 2.1.0 / Transformers 4.37.0 |
| 記憶體 | 3072 MB |
| 最大並發數 | 5 |
| 區域 | `us-east-2` |

### 檔案說明

| 檔案 | 說明 |
|------|------|
| `deploy_serverless_llm.py` | 建立 SageMaker Model、Endpoint Config、Serverless Endpoint，並測試冷啟動與暖機推論 |
| `invoke_endpoint.py` | 同時送出 5 個請求，分別計時每個推論的回應時間，並自動儲存結果 |

### 使用方式

#### 1. 部署

先設定你帳號的 SageMaker 執行角色 ARN（需具備 SageMaker 權限）：

```bash
export SAGEMAKER_EXECUTION_ROLE_ARN="arn:aws:iam::<你的帳號ID>:role/service-role/<你的角色>"
python deploy_serverless_llm.py
```

部署約需 5–10 分鐘。完成後會自動執行一次冷啟動測試和一次暖機測試。

#### 2. 並發推論

```bash
python invoke_endpoint.py
```

同時送出 5 個 prompt，按完成順序印出每個請求的回應時間，並自動儲存結果至帶時間戳記的 `.txt` 檔案。

```
同時送出 5 個請求...

[2] 1.65s | Machine learning helps us ...
[1] 1.73s | The future of AI is ...
[3] 1.84s | Cloud computing enables ...
[5] 1.88s | Natural language processing allows ...
[4] 20.12s | Deep learning models can ...

總等待時間（最慢那個）: 20.58s
```

### 延遲參考

| 狀態 | 延遲 |
|------|------|
| 冷啟動（idle 後第一次請求） | ~19–21s |
| 暖機推論 | ~1.7–2s |

---

## Part 2: Amazon Bedrock — Llama 3.1 8B Instruct

將自訂模型從 S3 匯入 Amazon Bedrock，並透過 API 呼叫。

### 概覽

| 項目 | 值 |
|------|-----|
| 模型 | `meta-llama/Llama-3.1-8B-Instruct` |
| 任務 | 對話 / 文字生成 |
| 服務 | Amazon Bedrock（自訂模型匯入） |
| 區域 | `us-east-2` |

### 檔案說明

| 檔案 | 說明 |
|------|------|
| `invoke_bedrock_llama.py` | 呼叫 Bedrock 上匯入的 Llama 模型，每 15 秒重試一次，最多等待 10 分鐘，並將冷啟動時間與推論時間記錄至 `.txt` 檔案 |

### 設定步驟

1. 從 Hugging Face 下載模型並上傳至 S3：
```bash
huggingface-cli login
python -c "
from huggingface_hub import snapshot_download
snapshot_download('meta-llama/Llama-3.1-8B-Instruct', local_dir='/tmp/llama-instruct')
"
aws s3 sync /tmp/llama-instruct s3://your-bucket/llama-3.1-8b-instruct/
```

2. 在 Bedrock Console → Imported models → Import model 匯入模型
   - Source：`s3://your-bucket/llama-3.1-8b-instruct/`
   - Service role 需有該 bucket 的 `s3:GetObject` 和 `s3:ListBucket` 權限

3. 記下你匯入模型的 ARN

### 使用方式

```bash
export BEDROCK_MODEL_ARN="arn:aws:bedrock:us-east-2:<你的帳號ID>:imported-model/<你的模型ID>"
python invoke_bedrock_llama.py
```

每 15 秒重試一次（最多 10 分鐘），模型就緒後呼叫並將結果儲存至帶時間戳記的 log 檔案。

### 延遲參考

| 狀態 | 延遲 |
|------|------|
| 冷啟動（模型未就緒） | ~4–7 分鐘 |
| 暖機推論 | ~0.6–1.3s |

---

## 前置需求

- AWS 帳號，IAM Role 需有 SageMaker 和 Bedrock 執行權限
- Hugging Face 帳號，並已申請 Llama 3.1 存取權
- Python 套件：`boto3`、`huggingface_hub`

```bash
pip install boto3 huggingface_hub
```
