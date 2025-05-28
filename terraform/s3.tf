resource "aws_s3_bucket" "data_bucket" {
  bucket = "my-app-data"
  acl    = "private"
}

# The previously public bucket policy is removed. 
# If you need to control access, create a policy granting access to specific AWS principals per least-privilege.