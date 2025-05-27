# services/feature_flags.py
# Define a set of allowed feature flags
ALLOWED_FEATURE_FLAGS = {
    'new_ui_enabled',
    'beta_feature',
    'dark_mode',
    'admin_dashboard',
    # Add other allowed feature flag names as needed
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Checks if the given feature flag is enabled.
    Returns True only if the flag_code is a valid, enabled feature flag.
    """
    if not isinstance(flag_code, str):
        return False
    return flag_code in ALLOWED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    params = event.get("queryStringParameters") or {}
    code = params.get("featureCheck", "")
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}