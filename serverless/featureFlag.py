# services/feature_flags.py
ENABLED_FEATURE_FLAGS = {"new_dashboard", "beta_feature", "dark_mode"}

def is_feature_enabled(flag_code: str) -> bool:
    return flag_code in ENABLED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}