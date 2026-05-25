import boto3
import json
import time

ENDPOINT_NAME = "distilgpt2-serverless"
REGION = "us-east-2"

runtime = boto3.client("sagemaker-runtime", region_name=REGION)

def invoke(prompt):
    start = time.time()
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps({"inputs": prompt}),
    )
    elapsed = time.time() - start
    result = json.loads(response["Body"].read())
    print(f"[{elapsed:.2f}s] {result[0]['generated_text']}\n")

# 第一次呼叫（可能冷啟動）
invoke("Tell me about machine learning")

# 第二次呼叫（暖機）
invoke("The best programming language is")
