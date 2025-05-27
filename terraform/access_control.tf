variable "trusted_ssh_cidr" {
  description = "CIDR block allowed to SSH. Limit this to your trusted IP range (e.g., office/public static IP)."
  type        = string
  default     = "0.0.0.0/0"
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted sources"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.trusted_ssh_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}