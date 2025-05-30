# services/feature_flags.py
FEATURE_FLAGS = {
    "flag_A": True,
    "flag_B": False,
    # Add additional feature flags here
}

def is_feature_enabled(flag_code: str) -> bool:
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}