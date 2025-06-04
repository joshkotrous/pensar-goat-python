# services/feature_flags.py
# A static mapping of valid feature codes to their enabled state
FEATURE_FLAGS = {
    "feature_x": True,
    "feature_y": False,
    "beta_feature": True,
    # Add more flag codes here as required
}

def is_feature_enabled(flag_code: str) -> bool:
    # Only allow checking for known feature codes, prevent code execution
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}