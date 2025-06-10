variable "allowed_ssh_cidr_blocks" {
  description = "List of CIDR blocks permitted to access SSH (port 22)"
  type        = list(string)
}

variable "allowed_egress_cidr_blocks" {
  description = "List of CIDR blocks permitted for outbound traffic"
  type        = list(string)
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from specified CIDR blocks"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    # Restrict SSH access to specified IP ranges only
    cidr_blocks = var.allowed_ssh_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    # Restrict egress traffic to specified destinations only
    cidr_blocks = var.allowed_egress_cidr_blocks
  }
}