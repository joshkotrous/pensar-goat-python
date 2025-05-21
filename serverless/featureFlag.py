# services/feature_flags.py
# Define the allowed feature flags and their enabled/disabled status.
FEATURE_FLAGS = {
    "new_dashboard": True,
    "beta_access": False,
    "dark_mode": True,
    # Add other feature flags as needed
}

def is_feature_enabled(flag_code: str) -> bool:
    # Only enable features explicitly defined as enabled in FEATURE_FLAGS
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}