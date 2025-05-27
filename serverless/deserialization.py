# services/token_service.py
import base64
import json


def decode_token(encoded):
    if not isinstance(encoded, str):
        raise ValueError("Session token must be a base64-encoded string")
    try:
        raw = base64.b64decode(encoded)
        # decode bytes to string
        data = raw.decode('utf-8')
        return json.loads(data)
    except Exception:
        # Optionally, log the exception here
        raise ValueError("Invalid session token")


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    return {"statusCode": 200, "body": str(session)}