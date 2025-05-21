# services/feature_flags.py
# Allowlist of known feature flags and their enabled/disabled status.
# Only these flag names are recognized and checked.
FEATURE_FLAGS = {
    "new_ui": True,
    "beta_mode": False,
    "logging_enabled": True,
    # Add other allowed feature flags here...
}


def is_feature_enabled(flag_code: str) -> bool:
    """
    Returns True if the passed flag_code is a valid, enabled feature flag.
    Only allowlisted flag names are checked. Arbitrary expressions are not evaluated.
    """
    # Only allow exact, known flag names, and return their value.
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}