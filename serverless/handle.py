# utils/aws_client.py
import boto3
# Pensar fix: Remove hard-coded AWS credentials. Use environment, config, or instance profile.


def get_s3_client():
    # boto3 will automatically use credentials from the environment or instance profile
    return boto3.client("s3")


# lambda_function.py
from utils.aws_client import get_s3_client


def handler(event, context):
    client = get_s3_client()
    return {"statusCode": 200, "body": "Client initialized"}