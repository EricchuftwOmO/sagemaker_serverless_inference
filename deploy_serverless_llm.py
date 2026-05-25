import boto3
import json
import time

ROLE = "arn:aws:iam::700694288831:role/service-role/AmazonSageMakerAdminIAMExecutionRole"
REGION = "us-east-2"
ENDPOINT_NAME = "distilgpt2-serverless"

sm = boto3.client("sagemaker", region_name=REGION)
runtime = boto3.client("sagemaker-runtime", region_name=REGION)

# HuggingFace DLC image for text-generation (CPU)
IMAGE_URI = "763104351884.dkr.ecr.us-east-2.amazonaws.com/huggingface-pytorch-inference:2.1.0-transformers4.37.0-cpu-py310-ubuntu22.04"

# 1. Create Model
print("Creating model...")
sm.create_model(
    ModelName=ENDPOINT_NAME,
    PrimaryContainer={
        "Image": IMAGE_URI,
        "Environment": {
            "HF_MODEL_ID": "distilgpt2",
            "HF_TASK": "text-generation",
        },
    },
    ExecutionRoleArn=ROLE,
)

# 2. Create Endpoint Config (Serverless)
print("Creating endpoint config...")
sm.create_endpoint_config(
    EndpointConfigName=ENDPOINT_NAME,
    ProductionVariants=[{
        "VariantName": "AllTraffic",
        "ModelName": ENDPOINT_NAME,
        "ServerlessConfig": {
            "MemorySizeInMB": 3072,
            "MaxConcurrency": 5,
        },
    }],
)

# 3. Create Endpoint
print("Deploying endpoint... (5-10 min)")
deploy_start = time.time()
sm.create_endpoint(EndpointName=ENDPOINT_NAME, EndpointConfigName=ENDPOINT_NAME)

# Wait for endpoint to be InService
waiter = sm.get_waiter("endpoint_in_service")
waiter.wait(EndpointName=ENDPOINT_NAME, WaiterConfig={"Delay": 30, "MaxAttempts": 30})
deploy_time = time.time() - deploy_start
print(f"Deployed in {deploy_time:.0f}s")

# 4. Test cold start
print("\nTesting cold start...")
cold_start = time.time()
response = runtime.invoke_endpoint(
    EndpointName=ENDPOINT_NAME,
    ContentType="application/json",
    Body=json.dumps({"inputs": "Hello, I am a language model"}),
)
cold_time = time.time() - cold_start
result = json.loads(response["Body"].read())
print(f"Cold start: {cold_time:.1f}s")
print(f"Result: {result}")

# 5. Test warm inference
print("\nTesting warm inference...")
warm_start = time.time()
response2 = runtime.invoke_endpoint(
    EndpointName=ENDPOINT_NAME,
    ContentType="application/json",
    Body=json.dumps({"inputs": "The future of AI is"}),
)
warm_time = time.time() - warm_start
result2 = json.loads(response2["Body"].read())
print(f"Warm inference: {warm_time:.1f}s")
print(f"Result: {result2}")

print(f"\nEndpoint: {ENDPOINT_NAME}")
