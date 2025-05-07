# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Only allow explicit, predefined feature codes
    enabled_features = {"new_feature", "beta_flag", "feature_x"}  # Add valid feature flag names here
    return flag_code in enabled_features


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}