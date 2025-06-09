# services/feature_flags.py

# Define a set of valid/known feature flag codes
ALLOWED_FEATURE_FLAGS = {
    "new_dashboard",
    "beta_user",
    "enable_api_v2"
    # Add more feature flags here as needed
}

def is_feature_enabled(flag_code: str) -> bool:
    # Only return True if the flag_code is an allowed feature flag
    return flag_code in ALLOWED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    query_params = event.get("queryStringParameters") or {}
    code = query_params.get("featureCheck", "")
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}