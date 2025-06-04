# services/token_service.py
import base64
import json


def decode_token(encoded):
    try:
        raw = base64.b64decode(encoded)
        session = json.loads(raw.decode('utf-8'))
        return session
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError, base64.binascii.Error):
        # Optionally, raise a custom exception or return None to handle bad tokens gracefully
        return None


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    if session is None:
        return {"statusCode": 400, "body": "Invalid or malformed session token."}
    return {"statusCode": 200, "body": str(session)}