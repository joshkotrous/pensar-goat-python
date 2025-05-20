resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

# The overly permissive public-read bucket policy has been removed.
# To enable access for specific principals, add a new, least-privilege policy block as needed.