# services/feature_flags.py
# Secure implementation: use a whitelist of allowed feature flags

# Example feature flags (update as appropriate for your use case)
ALLOWED_FEATURE_FLAGS = {
    "new_dashboard": True,
    "beta_access": False,
    "experimental_mode": False,
    # Add/update allowed features as needed
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Securely check if a specified feature flag is enabled.

    Args:
        flag_code (str): Feature flag code to check.

    Returns:
        bool: True if feature is enabled, False otherwise.
    """
    # Only allow checking predefined feature flags by exact name
    return ALLOWED_FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}