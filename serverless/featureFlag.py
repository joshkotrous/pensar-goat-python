# services/feature_flags.py
# A dictionary of all available feature flags and their enabled state.
FEATURE_FLAGS = {
    "NEW_UI_ENABLED": True,
    "BETA_FEATURE": False,
    # Add additional feature flags as needed.
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Checks if a given feature flag is enabled.
    Only allows flags explicitly defined in FEATURE_FLAGS.
    """
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}