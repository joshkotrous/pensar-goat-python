# services/token_service.py
import base64
import json


def decode_token(encoded):
    if not encoded:
        raise ValueError("Missing session token")
    try:
        raw = base64.b64decode(encoded)
        # JSON requires UTF-8 string
        raw_str = raw.decode('utf-8')
        return json.loads(raw_str)
    except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Invalid or corrupt session token")


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    return {"statusCode": 200, "body": str(session)}