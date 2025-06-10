# services/feature_flags.py
# Pensar fix: Disallow eval and only allow checking for known feature flags

# List or set of allowed/known feature flags considered enabled.
ENABLED_FEATURE_FLAGS = {
    "new_dashboard",   # example feature flags
    "beta_access",
    "dark_mode",
}

def is_feature_enabled(flag_code: str) -> bool:
    # Pensar fix: Only allow checking if flag_code is in the set of enabled flags
    return flag_code in ENABLED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}