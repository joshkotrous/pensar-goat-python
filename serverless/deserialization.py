# services/token_service.py
import base64
import json


def decode_token(encoded):
    if not encoded:
        return None
    try:
        raw = base64.b64decode(encoded)
        return json.loads(raw.decode('utf-8'))
    except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
        return None


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    if session is None:
        return {"statusCode": 400, "body": "Invalid session token."}
    return {"statusCode": 200, "body": str(session)}