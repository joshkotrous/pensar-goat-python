# services/token_service.py
import base64
import json


def decode_token(encoded):
    try:
        raw = base64.b64decode(encoded)
        # decode bytes to str, then parse as JSON
        session = json.loads(raw.decode('utf-8'))
        return session
    except (ValueError, json.JSONDecodeError, TypeError, base64.binascii.Error):
        # If any error occurs during decoding or deserialization, treat as invalid token.
        raise ValueError("Invalid session token format")


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    try:
        session = decode_token(token)
    except Exception:
        return {"statusCode": 400, "body": "Invalid session token"}
    return {"statusCode": 200, "body": str(session)}