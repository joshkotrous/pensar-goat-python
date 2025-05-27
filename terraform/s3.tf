resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

# Removed the aws_s3_bucket_policy resource that granted public read access.
# If access is needed, define a policy with least privilege for the appropriate principals.