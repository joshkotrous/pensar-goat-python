# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Define known feature flags here. Add/modify as applicable.
    enabled_flags = {
        "feature_x": True,
        "some_flag": False,
        # Add more feature flags as needed
    }
    return enabled_flags.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}