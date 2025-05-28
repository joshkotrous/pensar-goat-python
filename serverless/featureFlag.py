# services/feature_flags.py
# Define the set of enabled feature flags. In production, this could be loaded from config.
ENABLED_FEATURES = {
    "new_dashboard",
    "beta_api",
    "experimental_mode",
    # Add more allowed feature flags as needed.
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Checks whether the feature flag specified by flag_code is enabled.

    Args:
        flag_code (str): The name of the feature flag to check.

    Returns:
        bool: True if the feature is enabled, False otherwise.
    """
    return flag_code in ENABLED_FEATURES


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}