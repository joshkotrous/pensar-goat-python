resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  # Removed acl "public-read" to enforce private (default) bucket ACL
}

# Removed the overly permissive public bucket policy