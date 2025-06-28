# services/feature_flags.py

# Define a safe dictionary of feature flags and their enabled status
FEATURE_FLAGS = {
    "featureA": True,
    "featureB": False,
    # Add other feature flags here
}

def is_feature_enabled(flag_code: str) -> bool:
    # Instead of eval, safely check if the flag_code is in the allowed feature flags
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}
