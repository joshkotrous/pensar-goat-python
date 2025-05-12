` tag below.

**Changes and Rationale:**  
- **Removed hardcoded AWS credentials** from the `get_s3_client()` function in `utils/aws_client.py`.  
- The function now returns `boto3.client("s3")` with no explicit credentials.  
- No new imports or dependencies are introduced.
- All other logic is unchanged.  
- This approach is compatible with standard AWS credential management.

**Impact:**  
- Existing functionality remains unchanged, provided credentials are supplied to the environment via standard means.
- Developers/users must ensure AWS credentials are available in the runtime environment (IAM roles, environment variables, or credentials files).
- There is no impact on the `handler` logic or interface.

**Note:**  
If users previously relied on credentials being embedded in code, they must now configure credentials securely via the appropriate method for their environment.

</explanation>

<patch>
# utils/aws_client.py
import boto3


def get_s3_client():
    return boto3.client("s3")


# lambda_function.py
from utils.aws_client import get_s3_client


def handler(event, context):
    client = get_s3_client()
    return {"statusCode": 200, "body": "Client initialized"}
