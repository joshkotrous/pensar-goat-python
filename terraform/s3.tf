resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
}

# No public-read bucket policy is applied.
# If you require specific access, define a restrictive bucket policy here.