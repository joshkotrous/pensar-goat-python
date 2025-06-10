# Pensar fix
resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  # ACL set to private by omission (default - safest) [Pensar fix]
}

# Removed public bucket policy. [Pensar fix]