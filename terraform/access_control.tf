resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted sources"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_allowed_cidr]  # Restricted SSH source, variable must be set by user
  }

  # Restrict egress to only necessary ports (HTTP/HTTPS as an example)
  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Variable for allowed SSH source
variable "ssh_allowed_cidr" {
  type        = string
  description = "CIDR block allowed to access SSH on port 22 (e.g., 203.0.113.5/32 or office subnet)"
}