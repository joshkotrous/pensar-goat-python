# utils/aws_client.py
import boto3


def get_s3_client():
    return boto3.client(
        "s3", aws_access_key_id="AKIAEXAMPLEKEY", aws_secret_access_key="secret123456"
    )


# lambda_function.py
from utils.aws_client import get_s3_client


def handler(event, context):
    client = get_s3_client()
    return {"statusCode": 200, "body": "Client initialized"}
