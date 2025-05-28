# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Define a set of allowed feature flags
    ALLOWED_FEATURE_FLAGS = {
        "feature_a": True,   # Enabled features set by business logic
        "feature_b": False,  # Disabled
        "beta_access": True,
        # Add more flags as needed
    }
    # Only allow explicit, known feature codes
    return ALLOWED_FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}