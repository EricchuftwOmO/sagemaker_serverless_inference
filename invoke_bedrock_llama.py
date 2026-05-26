import boto3
import json
import time
from datetime import datetime

client = boto3.client("bedrock-runtime", region_name="us-east-2")
log_file = f"invoke_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
max_attempts = 40  # 40 * 15s = 600s = 10 minutes

script_start = time.time()

with open(log_file, "w") as f:
    f.write(f"Start time: {datetime.now()}\n\n")

for attempt in range(max_attempts):
    try:
        start = time.time()
        response = client.invoke_model(
            modelId="arn:aws:bedrock:us-east-2:700694288831:imported-model/39d4gt3a4z74",
            body=json.dumps({
                "messages": [{"role": "user", "content": "Tell me a joke"}],
                "max_gen_len": 512,
                "temperature": 0.7,
            })
        )
        elapsed = time.time() - start
        result = json.loads(response["body"].read())
        if "choices" in result:
            text = result["choices"][0]["message"]["content"]
        else:
            text = result.get("generation", str(result))

        cold_start = time.time() - script_start - elapsed

        print(text)
        print(f"\nCold start time: {cold_start:.1f}s")
        print(f"Inference time: {elapsed:.2f}s")

        with open(log_file, "a") as f:
            f.write(f"Success time: {datetime.now()}\n")
            f.write(f"Cold start time: {cold_start:.1f}s\n")
            f.write(f"Inference time: {elapsed:.2f}s\n\n")
            f.write(text)
        break

    except client.exceptions.ModelNotReadyException:
        msg = f"[{attempt+1}/{max_attempts}] Model not ready, retrying in 15s..."
        print(msg)
        with open(log_file, "a") as f:
            f.write(msg + "\n")
        time.sleep(15)
else:
    msg = "Waited 10 minutes, model still not ready."
    print(msg)
    with open(log_file, "a") as f:
        f.write(msg + "\n")

print(f"\nResults saved to: {log_file}")
