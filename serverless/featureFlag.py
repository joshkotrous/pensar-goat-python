# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Define allowed feature flags only
    ALLOWED_FLAGS = {
        "feature_x",
        "feature_y",
        "feature_z",
    }
    return flag_code in ALLOWED_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}