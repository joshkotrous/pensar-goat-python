# services/feature_flags.py
# Allowed feature flags and their enabled/disabled state.
_ALLOWED_FLAGS = {
    "new_ui": True,
    "beta_mode": False,
    "dark_mode": True
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Checks if the given feature flag is enabled.

    Args:
        flag_code (str): The flag to check.

    Returns:
        bool: True if the feature is enabled, False otherwise.
    """
    return _ALLOWED_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}