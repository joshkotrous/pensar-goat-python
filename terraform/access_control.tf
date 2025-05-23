variable "trusted_ssh_cidr_blocks" {
  description = "List of trusted CIDR blocks to allow SSH access (e.g., office, VPN, or bastion host IPs). Do not use 0.0.0.0/0."
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
    cidr_blocks = var.trusted_ssh_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}