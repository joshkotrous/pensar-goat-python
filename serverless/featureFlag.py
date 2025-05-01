# services/feature_flags.py
# Define a whitelist of enabled feature flag codes
ENABLED_FEATURE_FLAGS = {
    "new_dashboard",
    "beta_search",
    "enable_dark_mode",
    # Add further valid flag codes here as needed
}

def is_feature_enabled(flag_code: str) -> bool:
    # Only return True for specific, known feature flags
    return flag_code in ENABLED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"].get("featureCheck", "")
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}