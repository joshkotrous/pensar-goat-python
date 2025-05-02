# services/token_service.py
import base64
import json


def decode_token(encoded):
    if not encoded:
        raise ValueError("Missing session token.")
    try:
        raw = base64.b64decode(encoded)
        # Assume the raw data is a UTF-8 encoded JSON string
        session = json.loads(raw.decode('utf-8'))
        return session
    except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError("Invalid session token.") from e


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    try:
        session = decode_token(token)
        return {"statusCode": 200, "body": str(session)}
    except ValueError as e:
        return {"statusCode": 400, "body": str(e)}