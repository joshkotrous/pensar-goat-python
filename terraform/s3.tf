resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

# Removed aws_s3_bucket_policy that granted public read access.