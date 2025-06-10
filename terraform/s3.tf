resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  # Removed ACL to avoid public read access
}

# Removed overly permissive public-read bucket policy
# If you need to grant access, define specific principals and permissions here
# Example (commented out/no public access):
# resource "aws_s3_bucket_policy" "data_policy" {
#   bucket = aws_s3_bucket.data_bucket.id
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = []
#   })
# }