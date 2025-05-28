# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    """
    Returns whether a given feature is enabled.
    Only allows checking against known, predefined feature names.
    """
    FEATURE_FLAGS = {
        "featureA": True,
        "featureB": False,
        "featureC": True,
        # Add valid feature names as required.
    }
    return FEATURE_FLAGS.get(flag_code, False)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}