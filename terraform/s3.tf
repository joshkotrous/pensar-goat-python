resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  # Removed overly permissive ACL. The default ACL ("private") now applies.
}

# Removed public bucket policy to prevent public read access.