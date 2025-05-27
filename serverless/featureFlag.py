# services/feature_flags.py
# Define a set of allowed feature flags
_ALLOWED_FEATURE_FLAGS = {
    "new_ui": True,
    "beta_payment": False,
    # Add more flags as needed
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Check if the given feature flag is enabled.

    Args:
        flag_code (str): The code/name of the feature flag.

    Returns:
        bool: True if the feature is enabled; False otherwise.
    """
    # Only allow checking simple feature flag names
    return _ALLOWED_FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}