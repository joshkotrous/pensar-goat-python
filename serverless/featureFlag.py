# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Whitelisted features and their enabled status
    _FEATURE_FLAGS = {
        "new_dashboard": True,
        "beta_mode": False,
        "experimental_payments": False,
        # Add other feature flags as needed
    }
    return _FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}