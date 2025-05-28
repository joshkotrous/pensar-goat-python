# services/token_service.py
import base64
import json


def decode_token(encoded):
    try:
        raw = base64.b64decode(encoded)
        json_str = raw.decode("utf-8")
        return json.loads(json_str)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError, base64.binascii.Error) as e:
        raise ValueError("Invalid session token") from e


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    try:
        session = decode_token(token)
        return {"statusCode": 200, "body": str(session)}
    except Exception:
        return {"statusCode": 400, "body": "Invalid session token"}