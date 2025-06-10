# Pensar fix: Removed public 'acl' and public bucket policy to close open access.

resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  # acl    = "public-read" # Pensar fix: Removed to ensure bucket is private by default
}

# Pensar fix: Removed insecure aws_s3_bucket_policy that granted public read access
# If public or shared access is needed, define a restricted policy with specific principals and actions.