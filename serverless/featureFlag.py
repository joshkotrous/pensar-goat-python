# services/feature_flags.py
FEATURE_FLAGS = {
    "feature_a": True,
    "feature_b": False,
    "beta_user": True,
    # Add further legitimate feature flags here
}


def is_feature_enabled(flag_code: str) -> bool:
    """
    Securely checks if a feature flag is enabled.
    Only recognized feature flag names (as strings) are accepted.
    """
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"].get("featureCheck", "")
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}