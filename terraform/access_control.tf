variable "allowed_ssh_cidr_blocks" {
  description = "List of CIDR blocks allowed to access SSH. Restrict to your trusted IPs or networks (e.g., ['203.0.113.0/24'])."
  type        = list(string)
  default     = []
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from restricted CIDR blocks"
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