resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

# Bucket policy removed to eliminate public access