variable "allowed_ssh_cidrs" {
  description = "List of CIDR blocks allowed SSH access (port 22). Example: [\"203.0.113.10/32\"]"
  type        = list(string)
  default     = []
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from specified CIDRs"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}