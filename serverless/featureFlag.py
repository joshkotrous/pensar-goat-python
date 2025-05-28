# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Define a whitelist of allowed feature flag codes
    ALLOWED_FEATURE_FLAGS = {
        "ENABLE_NEW_DASHBOARD",
        "BETA_USER_ACCESS",
        "EXPERIMENTAL_FEATURE_X",
        # Add any other valid feature codes here
    }
    # Only enable the feature if the flag_code matches an allowed feature
    return flag_code in ALLOWED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}