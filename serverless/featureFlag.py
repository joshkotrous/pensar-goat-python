# services/feature_flags.py
# Define a safe set or dictionary of enabled feature flags
ENABLED_FEATURE_FLAGS = {
    "feature1": True,
    "feature2": True,
    # Add other feature flags here
}

def is_feature_enabled(flag_code: str) -> bool:
    # Instead of eval, safely check if the flag_code is in the enabled flags
    return ENABLED_FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}
