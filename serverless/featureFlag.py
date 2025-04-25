# services/feature_flags.py
# Define known feature flags and their enabled status.
FEATURE_FLAGS = {
    "new_UI": True,
    "beta_feature": False,
    "dark_mode": True,
    # Add other valid feature flag keys and their status as needed.
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Securely checks if a given feature flag is enabled.
    Only returns True if `flag_code` exactly matches a known feature flag key and is enabled.
    """
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}