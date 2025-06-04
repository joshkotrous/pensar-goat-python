resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

resource "aws_s3_bucket_policy" "data_policy" {
  bucket = aws_s3_bucket.data_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # The public-read allow statement is removed. Replace or extend with restrictive
      # statements as needed for specific AWS principals.
    ]
  })
}