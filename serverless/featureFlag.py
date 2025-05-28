# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    """
    Checks whether the feature flag with the provided name is enabled.

    Only allows checking for known features by name; does not evaluate arbitrary code.
    """
    # Define allowed feature flags and their enabled status
    enabled_flags = {
        "feature_x": True,
        "feature_y": False,
        # Add more feature flags as needed
    }
    return enabled_flags.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    query_params = event.get("queryStringParameters", {})
    code = query_params.get("featureCheck")
    if code and is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}