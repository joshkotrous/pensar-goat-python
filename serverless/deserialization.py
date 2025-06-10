# services/token_service.py
import base64
import json


def decode_token(encoded):
    try:
        raw = base64.b64decode(encoded)
        return json.loads(raw.decode('utf-8'))
    except (ValueError, TypeError, json.JSONDecodeError, base64.binascii.Error):
        return None


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    return {"statusCode": 200, "body": str(session)}