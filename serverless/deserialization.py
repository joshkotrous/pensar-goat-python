# services/token_service.py
import base64
import json


def decode_token(encoded):
    try:
        raw = base64.b64decode(encoded)
        decoded = raw.decode('utf-8')
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        # Return None or raise custom error as per application policy
        return None


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    if not token:
        return {"statusCode": 400, "body": "Missing or invalid session token."}
    session = decode_token(token)
    if session is None:
        return {"statusCode": 400, "body": "Invalid session token."}
    return {"statusCode": 200, "body": str(session)}