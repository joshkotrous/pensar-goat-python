# services/token_service.py
import base64
import json


def decode_token(encoded):
    try:
        raw = base64.b64decode(encoded)
        return json.loads(raw.decode('utf-8'))
    except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError("Invalid session token") from e


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    try:
        session = decode_token(token)
    except Exception:
        return {"statusCode": 400, "body": "Invalid session token"}
    return {"statusCode": 200, "body": str(session)}