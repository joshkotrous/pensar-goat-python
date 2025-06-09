# services/feature_flags.py
ALLOWED_FEATURE_FLAGS = {"new_dashboard", "beta_feature", "user_uploads"}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Checks if the provided feature flag code is enabled.
    Only allows explicit, pre-defined flag codes for safety.
    """
    return flag_code in ALLOWED_FEATURE_FLAGS


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = None
    params = event.get("queryStringParameters")
    if params and "featureCheck" in params:
        code = params["featureCheck"]
    if code and is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}