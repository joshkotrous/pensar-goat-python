resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from restricted source(s)"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.ssh_allowed_cidrs
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

variable "ssh_allowed_cidrs" {
  description = "List of CIDR blocks allowed SSH access (e.g., your office IP or VPN range). Must NOT be 0.0.0.0/0."
  type        = list(string)
  default     = []
  validation {
    condition     = length([for cidr in var.ssh_allowed_cidrs : cidr if cidr == "0.0.0.0/0"]) == 0
    error_message = "For security reasons, you must not allow SSH (port 22) from '0.0.0.0/0'. Specify only trusted IP ranges."
  }
}