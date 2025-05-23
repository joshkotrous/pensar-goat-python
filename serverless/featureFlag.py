# services/feature_flags.py
# Define allowed feature flags and their enablement state
FEATURE_FLAGS = {
    "new_dashboard": True,
    "beta_user": False,
    "enable_payments": True,
    # Add more feature flags as necessary
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Checks if a feature flag is enabled.

    Args:
        flag_code (str): The feature flag code/name to check.

    Returns:
        bool: True if the feature flag is enabled, False otherwise.
    """
    # Only allow simple, predefined feature flag codes
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}