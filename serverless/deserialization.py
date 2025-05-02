# services/token_service.py
import base64
import json


def decode_token(encoded):
    if not isinstance(encoded, str):
        raise ValueError("Token must be a base64-encoded string")
    try:
        raw = base64.b64decode(encoded)
    except Exception as e:
        raise ValueError("Invalid base64-encoded token") from e
    try:
        # Decode to str (UTF-8), then parse JSON
        json_data = raw.decode('utf-8')
        return json.loads(json_data)
    except Exception as e:
        raise ValueError("Invalid token format") from e


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    if token is None:
        return {"statusCode": 400, "body": "Missing session token"}
    try:
        session = decode_token(token)
    except Exception as e:
        return {"statusCode": 400, "body": "Invalid session token"}
    return {"statusCode": 200, "body": str(session)}