resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  # Removed the 'public-read' ACL to ensure bucket is private by default
}

# Removed public bucket policy that allowed anyone s3:GetObject access