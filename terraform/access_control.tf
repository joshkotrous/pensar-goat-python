variable "allowed_ssh_cidr_blocks" {
  description = "List of CIDR blocks allowed SSH access (port 22). Specify trusted networks only."
  type        = list(string)
  default     = []
}

variable "allowed_egress_cidr_blocks" {
  description = "List of CIDR blocks allowed for egress traffic."
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted networks"
  vpc_id      = var.vpc_id

  # Ingress: Only allow SSH from explicitly specified trusted sources
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr_blocks
  }

  # Egress: Allow custom restriction of outbound traffic via variable
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.allowed_egress_cidr_blocks
  }
}