# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    """
    Check if the given feature flag code is enabled.

    Only allows a predefined list of safe feature flag names.
    """
    ENABLED_FEATURE_FLAGS = {"feature_a", "feature_b", "feature_c"}  # Example: adjust as needed
    return flag_code in ENABLED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}