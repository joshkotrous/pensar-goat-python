# utils/aws_client.py
import os
import boto3


def get_s3_client():
    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    client_args = {}
    if aws_access_key_id and aws_secret_access_key:
        client_args['aws_access_key_id'] = aws_access_key_id
        client_args['aws_secret_access_key'] = aws_secret_access_key
    return boto3.client("s3", **client_args)


# lambda_function.py
from utils.aws_client import get_s3_client


def handler(event, context):
    client = get_s3_client()
    return {"statusCode": 200, "body": "Client initialized"}