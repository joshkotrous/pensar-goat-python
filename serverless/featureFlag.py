# services/feature_flags.py

FEATURE_FLAGS = {
    "beta_feature": True,
    "dark_mode": False,
    "new_dashboard": True,
}

def is_feature_enabled(flag_code: str) -> bool:
    """
    Safely checks if a feature flag is enabled.
    Only feature flags defined in FEATURE_FLAGS are valid.
    """
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py

from services.feature_flags import is_feature_enabled


def handler(event, context):
    query_params = event.get("queryStringParameters") or {}
    code = query_params.get("featureCheck", "")
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}