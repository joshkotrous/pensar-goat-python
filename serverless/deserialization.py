# services/token_service.py
import base64
import json


def decode_token(encoded):
    if encoded is None:
        raise ValueError("Missing session token")
    try:
        raw = base64.b64decode(encoded)
        # Safely load the decoded data as JSON, not pickle
        return json.loads(raw.decode('utf-8'))
    except (ValueError, json.JSONDecodeError, base64.binascii.Error) as e:
        raise ValueError("Invalid session token") from e


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    try:
        session = decode_token(token)
        return {"statusCode": 200, "body": str(session)}
    except ValueError:
        return {"statusCode": 400, "body": "Invalid session token"}