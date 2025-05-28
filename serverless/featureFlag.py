# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Replace eval with explicit mapping for feature flags
    enabled_flags = {
        "feature_x_enabled": True,
        "feature_y_enabled": False,
        # Add further valid feature flags as needed
    }
    return enabled_flags.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}