variable "trusted_ssh_cidr_blocks" {
  description = "List of trusted CIDRs allowed to access SSH (port 22)."
  type        = list(string)
  # Set a secure default (empty) – users must override for admin access
  default     = []
}

variable "allowed_egress_cidr_blocks" {
  description = "List of CIDRs allowed as outbound destination. Restrict to only what's required."
  type        = list(string)
  # Example: Allow HTTPS out to anywhere
  default     = ["0.0.0.0/0"]
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted sources"
  vpc_id      = var.vpc_id

  # Restrict SSH ingress to trusted sources only
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.trusted_ssh_cidr_blocks
  }

  # Limit egress to HTTPS (443) by default; users can override as needed.
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.allowed_egress_cidr_blocks
  }
}
