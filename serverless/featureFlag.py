# services/feature_flags.py
from typing import Set

# Define allowed feature flags here
_ENABLED_FEATURE_FLAGS: Set[str] = {
    "NEW_DASHBOARD",
    "ENABLE_BETA",
    "USE_EXPERIMENTAL_API",
    # Add any additional valid feature flags here
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Safely checks if a feature is enabled by looking for the flag name
    in the allowed set. No code execution occurs.
    """
    if not isinstance(flag_code, str):
        return False
    return flag_code in _ENABLED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    params = event.get("queryStringParameters") or {}
    code = params.get("featureCheck", "")
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}