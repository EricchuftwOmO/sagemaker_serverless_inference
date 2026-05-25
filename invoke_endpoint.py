import boto3
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ENDPOINT_NAME = "distilgpt2-serverless"
REGION = "us-east-2"

PROMPTS = [
    "The future of AI is",
    "Machine learning helps us",
    "Cloud computing enables",
    "Deep learning models can",
    "Natural language processing allows",
]

def invoke(i, prompt):
    runtime = boto3.client("sagemaker-runtime", region_name=REGION)
    t0 = time.time()
    response = runtime.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps({"inputs": prompt}),
    )
    elapsed = time.time() - t0
    result = json.loads(response["Body"].read())
    return i, elapsed, result[0]["generated_text"]

print("同時送出 5 個請求...\n")
wall_start = time.time()
lines = []

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(invoke, i, p) for i, p in enumerate(PROMPTS)]
    for future in as_completed(futures):
        i, elapsed, text = future.result()
        line = f"[{i+1}] {elapsed:.2f}s | {text[:80]}"
        print(line)
        lines.append(line)

summary = f"\n總等待時間（最慢那個）: {time.time() - wall_start:.2f}s"
print(summary)

filename = f"result_{time.strftime('%Y%m%d_%H%M%S')}.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write("Sending 5 concurrent requests...\n\n")
    f.write("\n".join(lines))
    f.write(f"\n\nTotal wall time (slowest): {time.time() - wall_start:.2f}s\n")
print(f"\nResults saved to {filename}")
