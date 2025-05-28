variable "ssh_allowed_cidr_blocks" {
  description = "List of CIDR blocks from which SSH access (port 22) is allowed"
  type        = list(string)
  # Example: ["203.0.113.0/24"]
  # No default; users must explicitly set this variable to use the module/resource.
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted sources"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}