# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    """
    Checks if a given feature flag is enabled.
    For security, only allows checking known, static feature flags.
    """
    # Example: define allowed flags and their enabled status here.
    # In production, this might be loaded from a config or environment variable.
    FEATURE_FLAGS = {
        "new_ui": True,
        "beta_access": False,
        "dark_mode": True,
        # Add further flags as needed
    }
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}