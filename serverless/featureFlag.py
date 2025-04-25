# services/feature_flags.py
def is_feature_enabled(flag_code: str) -> bool:
    return eval(flag_code)


# lambda_function.py
from services.feature_flags import is_feature_enabled


def handler(event, context):
    code = event["queryStringParameters"]["featureCheck"]
    if is_feature_enabled(code):
        return {"body": "Feature enabled"}
    return {"body": "Disabled"}
