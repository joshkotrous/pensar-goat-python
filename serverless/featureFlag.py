# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Check if the given flag_code is in the list of enabled features
    # Define an example set of enabled feature flags (to be modified as needed)
    enabled_features = {"beta_feature", "new_ui", "experimental_login"}
    return flag_code in enabled_features


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    # Defensive: extract queryStringParameters safely in case it's missing
    query_params = event.get("queryStringParameters") or {}
    code = query_params.get("featureCheck")
    if code and is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}