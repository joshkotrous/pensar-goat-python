# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    """
    Check if the given feature flag is enabled.
    Only known/allowed flags are supported.
    """
    # Define your feature flags and their enabled/disabled status here
    FEATURE_FLAGS = {
        "new_dashboard": True,
        "beta_user": False,
        "enable_payments": True,
        # Add further flags as needed
    }

    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}