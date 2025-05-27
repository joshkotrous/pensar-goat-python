variable "allowed_ssh_cidr_blocks" {
  description = "List of trusted CIDR blocks allowed to access SSH (port 22)"
  type        = list(string)
  # Replace with your organization's trusted IP range(s). Example provided:
  default     = ["203.0.113.0/24"]
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted CIDR blocks"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr_blocks
    # Restrict SSH access to known trusted addresses only.
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    # Allow outbound HTTPS only. Adjust as necessary for minimum required egress.
  }

  # Additional egress rules can be defined here if specific outbound access is needed.
}