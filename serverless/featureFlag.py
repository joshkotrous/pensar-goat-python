# services/feature_flags.py

# Define a whitelist of allowed feature flags and their states
FEATURE_FLAGS = {
    "new_dashboard": True,
    "beta_mode": False,
    # Add other feature flags as needed
}

def is_feature_enabled(flag_code: str) -> bool:
    # Only allow feature checking by name, never code evaluation
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled

def handler(event, context):
    code = event["queryStringParameters"].get("featureCheck")
    if not code:
        return {"body": "Disabled"}
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}