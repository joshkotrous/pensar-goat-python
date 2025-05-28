# services/token_service.py
import base64
import json


def decode_token(encoded):
    try:
        raw = base64.b64decode(encoded)
        # Ensure the raw data is a UTF-8 string for JSON
        session = json.loads(raw.decode('utf-8'))
        return session
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        # Invalid token format, raise or return None/empty
        # For security, avoid leaking details
        return None


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    if session is None:
        return {"statusCode": 400, "body": "Invalid session token"}
    return {"statusCode": 200, "body": str(session)}