variable "allowed_ssh_cidr_blocks" {
  description = "List of CIDR blocks permitted to access SSH (port 22). Update this with your trusted network(s)."
  type        = list(string)
  # Pensar fix: Default is a non-public documentation network; must be overridden in production for SSH access
  default     = ["192.0.2.0/24"]
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from restricted CIDR blocks"
  vpc_id      = var.vpc_id

  ingress {
    # Pensar fix: Restrict SSH ingress to trusted network(s), not open to all
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