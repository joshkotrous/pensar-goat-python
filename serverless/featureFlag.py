# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Pensar fix: Use a whitelist for valid feature flags, never eval user input
    ALLOWED_FEATURE_FLAGS = {
        "beta_feature_1",
        "dark_mode",
        "new_dashboard",
        # Add other legitimate feature codes here
    }
    return flag_code in ALLOWED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}