variable "allowed_ssh_cidr_blocks" {
  description = "List of allowed CIDR blocks for SSH ingress (port 22). Should be restricted to trusted IP addresses or ranges."
  type        = list(string)
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted IP ranges"
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