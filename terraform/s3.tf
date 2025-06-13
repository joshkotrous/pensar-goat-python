resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  # Removed acl = "public-read" to prevent public access; defaults to private
}

# Removed the bucket policy that allowed public read access.