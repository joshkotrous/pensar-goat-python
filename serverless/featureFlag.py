# services/feature_flags.py
# Define known feature flags and their enabled status.
# Example: {"new_ui": True, "beta_mode": False}.
FEATURE_FLAGS = {
    "new_ui": True,
    "beta_mode": False,
    # Add other valid feature flags here.
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Checks if a feature flag is enabled based on a predefined whitelist.
    Args:
        flag_code (str): The name of the feature flag to check.
    Returns:
        bool: True if the feature is enabled, False if not found or disabled.
    """
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}