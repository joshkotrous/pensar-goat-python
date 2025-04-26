# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Define a set of allowed feature flags
    allowed_flags = {"new_checkout", "beta_user_experience", "advanced_search"}
    return flag_code in allowed_flags


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}