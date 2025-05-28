resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  # Removed public-read ACL to restrict public access; defaults to private
}

# Removed the public bucket policy to eliminate public read access.
# If specific access is needed, define a restrictive policy 
# with minimum required permissions to trusted principals only.