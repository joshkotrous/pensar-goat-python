# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Define allowed feature flag codes
    enabled_features = {
        'new_checkout',
        'beta_user',
        'feature_x'
        # Add other valid feature codes here as needed
    }
    # Return True if the requested feature is enabled
    return flag_code in enabled_features


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}