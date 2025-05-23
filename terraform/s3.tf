resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

# Removed overly permissive bucket policy that granted public read access.
# If additional, more restrictive access is needed, add a specific bucket policy here.