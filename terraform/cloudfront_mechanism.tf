resource "aws_cloudfront_distribution" "no_waf" {
  origin {
    domain_name = "example.s3.amazonaws.com"
    origin_id   = "s3-origin"
  }

  enabled = true

  default_cache_behavior {
    target_origin_id = "s3-origin"
    viewer_protocol_policy = "redirect-to-https"  # Enforces HTTPS, mitigates CWE-319
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  # ❗ No AWS WAF attached to protect against application attacks
}