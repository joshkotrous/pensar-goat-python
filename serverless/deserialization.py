# services/token_service.py
import base64
import json


def decode_token(encoded):
    if not isinstance(encoded, str):
        raise ValueError("Session token must be a base64-encoded string")
    try:
        raw = base64.b64decode(encoded)
        return json.loads(raw.decode('utf-8'))
    except (ValueError, json.JSONDecodeError, base64.binascii.Error) as e:
        raise ValueError("Invalid session token") from e


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    if token is None:
        return {"statusCode": 400, "body": "Missing session token"}
    try:
        session = decode_token(token)
    except ValueError:
        return {"statusCode": 400, "body": "Invalid session token"}
    return {"statusCode": 200, "body": str(session)}