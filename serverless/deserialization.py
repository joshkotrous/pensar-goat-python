# services/token_service.py
import base64
import pickle
import io


class SafeUnpickler(pickle.Unpickler):
    # Whitelist of safe classes
    safe_builtins = {
        'builtins': {
            'set', 'frozenset', 'complex', 'dict', 'list', 'tuple', 'str', 'int', 'float', 'bool', 'NoneType'
        }
    }

    def find_class(self, module, name):
        if module in self.safe_builtins and name in self.safe_builtins[module]:
            return super().find_class(module, name)
        # Forbid everything else
        raise pickle.UnpicklingError(f"Global '{module}.{name}' is forbidden")


def decode_token(encoded):
    raw = base64.b64decode(encoded)
    file_like = io.BytesIO(raw)
    return SafeUnpickler(file_like).load()


# lambda_function.py
from services.token_service import decode_token


def handler(event, context):
    token = event.get("headers", {}).get("X-Session-Token")
    session = decode_token(token)
    return {"statusCode": 200, "body": str(session)}
