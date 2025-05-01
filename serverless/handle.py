# utils/aws_client.py
import boto3
import os


def get_s3_client():
    # Credentials are now retrieved by boto3 from environment variables or IAM role
    return boto3.client("s3")


# lambda_function.py
from utils.aws_client import get_s3_client


def handler(event, context):
    client = get_s3_client()
    return {"statusCode": 200, "body": "Client initialized"}