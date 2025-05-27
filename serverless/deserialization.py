# services/token_service.py
import base64
import json


def decode_token(encoded):
    if not isinstance(encoded, str):
        raise ValueError("Token must be a base64-encoded string")
    try:
        raw = base64.b64decode(encoded)
    except Exception:
        raise ValueError("Invalid base64-encoded token")
    try:
        # Ensure safe deserialization using JSON instead of pickle
        return json.loads(raw.decode('utf-8'))
    except Exception:
        raise ValueError("Session token is not valid JSON")


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    if token is None:
        return {"statusCode": 400, "body": "Missing X-Session-Token header"}
    try:
        session = decode_token(token)
    except Exception as e:
        return {"statusCode": 400, "body": "Invalid session token"}
    return {"statusCode": 200, "body": str(session)}