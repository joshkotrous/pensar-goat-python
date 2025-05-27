# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Define allowed feature flags
    enabled_features = {
        "feature_login": True,
        "feature_beta": False,
        "feature_dark_mode": True,
        # Add additional feature flags here as needed
    }
    return enabled_features.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}