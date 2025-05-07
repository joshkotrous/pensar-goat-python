resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

# The insecure public-read bucket policy has been removed. If custom access is needed,
# define a more restrictive policy targeting trusted AWS principals.