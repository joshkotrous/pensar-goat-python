resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

# Removed aws_s3_bucket_policy granting public read access.
# If controlled access is needed, define a more restrictive policy here.