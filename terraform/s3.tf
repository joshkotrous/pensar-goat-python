resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "public-read" 
}

resource "aws_s3_bucket_policy" "data_policy" {
  bucket = aws_s3_bucket.data_bucket.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicRead"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.data_bucket.arn}/*"
      }
    ]
  })
}
