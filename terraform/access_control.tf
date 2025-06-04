variable "ssh_allowed_cidr" {
  description = "CIDR block(s) from which SSH (port 22) is allowed. Replace default with your trusted IPs."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

resource "aws_security_group" "ssh_restricted" {
  name        = "restricted_ssh"
  description = "Allow SSH from trusted sources"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidr
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}