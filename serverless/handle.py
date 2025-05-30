# utils/aws_client.py
import boto3


def get_s3_client():
    # Use default credential lookup (environment, shared credentials, etc.)
    return boto3.client("s3")


# lambda_function.py
from utils.aws_client import get_s3_client


def handler(event, context):
    client = get_s3_client()
    return {"statusCode": 200, "body": "Client initialized"}