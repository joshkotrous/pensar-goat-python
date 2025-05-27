# services/token_service.py
import base64
import json


def decode_token(encoded):
    if not isinstance(encoded, str):
        raise ValueError("Token must be a string")
    try:
        raw = base64.b64decode(encoded)
        # In Python3, base64.b64decode returns bytes; decode to string
        json_str = raw.decode('utf-8')
        return json.loads(json_str)
    except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        # Hide details, just mark token as invalid
        raise ValueError("Invalid session token") from e


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    try:
        session = decode_token(token)
        return {"statusCode": 200, "body": str(session)}
    except Exception:
        return {"statusCode": 400, "body": "Invalid session token"}