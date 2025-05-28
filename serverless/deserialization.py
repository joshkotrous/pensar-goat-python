# services/token_service.py
import base64
import json


def decode_token(encoded):
    try:
        if encoded is None:
            return None
        raw = base64.b64decode(encoded)
        # Expect the session token to be a JSON-serialized object.
        return json.loads(raw.decode('utf-8'))
    except (ValueError, json.JSONDecodeError, base64.binascii.Error):
        # Invalid base64 or invalid JSON
        return None


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    if session is None:
        return {
            "statusCode": 400,
            "body": "Invalid or missing session token"
        }
    return {"statusCode": 200, "body": str(session)}