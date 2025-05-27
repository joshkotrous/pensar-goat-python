# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # List of allowed feature flags
    enabled_flags = {
        "new_ui",
        "beta_access",
        "discount_enabled",
        "advanced_search",
        # Add other known flag names here as needed
    }
    return flag_code in enabled_flags


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}