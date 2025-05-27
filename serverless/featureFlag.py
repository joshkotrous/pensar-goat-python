# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    """
    Safely checks if the requested feature flag is enabled.
    Only allows a restricted set of known flags or boolean values.
    Returns True only for recognized enabled values.
    """
    # Example: define a set of accepted feature flags that are enabled
    ENABLED_FEATURE_FLAGS = {"new_dashboard", "user_profiles"}  # extend as needed

    # Normalize the user input
    value = flag_code.strip().lower()

    # Allow explicit boolean values
    if value in ("true", "1", "yes", "on"):
        return True
    if value in ("false", "0", "no", "off"):
        return False

    # Allow only known feature codes
    if value in ENABLED_FEATURE_FLAGS:
        return True

    # If flag is not recognized, consider it disabled
    return False


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}