# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    # Define allowed feature flags and their enabled status.
    FEATURE_FLAGS = {
        "new_dashboard": True,
        "beta_feature": False,
        "experimental_ui": False,
        # Add more known flags here
    }
    # Only return True if the flag_code is a known key and enabled
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    params = event.get("queryStringParameters", {})
    code = params.get("featureCheck", "")
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}