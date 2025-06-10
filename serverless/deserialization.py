# services/token_service.py
import base64
import json  # Pensar fix


def decode_token(encoded):
    # Pensar fix: Use JSON instead of pickle for safe deserialization
    raw = base64.b64decode(encoded)
    return json.loads(raw)


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    return {"statusCode": 200, "body": str(session)}