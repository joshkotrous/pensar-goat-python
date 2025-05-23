# services/token_service.py
import base64
import json


def decode_token(encoded):
    try:
        raw = base64.b64decode(encoded)
        session = json.loads(raw.decode('utf-8'))
        return session
    except (ValueError, json.JSONDecodeError, TypeError, base64.binascii.Error):
        # Handle decoding errors; in real-world usage, consider logging or customizing this response
        return None


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    return {"statusCode": 200, "body": str(session)}