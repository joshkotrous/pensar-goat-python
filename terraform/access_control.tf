variable "ssh_allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access SSH (port 22). Should be restricted to trusted IP ranges, e.g., office or VPN."
  type        = list(string)
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted networks"
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