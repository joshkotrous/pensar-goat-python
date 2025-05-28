# services/feature_flags.py
# Secure implementation: Only allow valid feature flag codes.
from typing import Set

# Example set of valid feature flag names
VALID_FEATURE_FLAGS: Set[str] = {
    "beta_dashboard",
    "experimental_search",
    "dark_mode",
    "new_upload_ui",
    # Add more valid feature flag codes here as needed
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Check if the given feature flag code is enabled.

    Args:
        flag_code (str): The code/name of the feature flag to check.

    Returns:
        bool: True if the feature flag is enabled, False otherwise.
    """
    return flag_code in VALID_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}