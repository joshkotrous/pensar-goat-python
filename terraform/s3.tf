resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

# The following policy is removed to eliminate public read access.
# If specific, limited access is required, define a more restrictive bucket policy as needed.