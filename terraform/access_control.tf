variable "allowed_ssh_cidr_blocks" {
  description = "List of CIDR blocks from which SSH (port 22) access is allowed. For maximum security, restrict to specific IP(s) (e.g., ['203.0.113.25/32'])."
  type        = list(string)
  # No default provided to force explicit specification and ensure secure access control
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from specified CIDR blocks"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}