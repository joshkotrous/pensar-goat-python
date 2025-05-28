variable "allowed_ssh_cidr_blocks" {
  description = "List of CIDR blocks allowed to access SSH (port 22). Example: [\"203.0.113.0/24\", \"198.51.100.5/32\"]"
  type        = list(string)
  default     = []
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted sources"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr_blocks
    description = "SSH access from trusted locations"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.allowed_ssh_cidr_blocks
    description = "Outbound traffic allowed to trusted networks"
  }
}