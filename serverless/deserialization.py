# services/token_service.py
import base64
import json  # Pensar fix: switched from pickle to json for safe deserialization


def decode_token(encoded):
    """
    Decodes a base64-encoded JSON session token safely.
    Pensar fix: switched from pickle.loads() to json.loads() for security.
    """
    try:
        raw = base64.b64decode(encoded)
        # Pensar fix: json is safe for untrusted data, unlike pickle.
        return json.loads(raw.decode('utf-8'))
    except Exception:
        # Pensar fix: fail closed if data is invalid/malformed
        return None


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    if session is None:
        return {"statusCode": 400, "body": "Invalid session token"}
    return {"statusCode": 200, "body": str(session)}