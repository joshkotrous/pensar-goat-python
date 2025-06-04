# utils/aws_client.py
import boto3


def get_s3_client():
    # Do not hardcode credentials; rely on Boto3's default credential chain
    return boto3.client("s3")


# lambda_function.py
from utils.aws_client import get_s3_client


def handler(event, context):
    client = get_s3_client()
    return {"statusCode": 200, "body": "Client initialized"}