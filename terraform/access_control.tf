resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from specified IPs"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    # Pensar fix: Restrict SSH ingress to trusted IPs/subnets (do not allow 0.0.0.0/0)
    cidr_blocks = var.ssh_allowed_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Pensar fix: You should define var.ssh_allowed_cidr_blocks in your variables.tf like:
# variable "ssh_allowed_cidr_blocks" {
#   description = "List of CIDR blocks allowed to SSH (default is your corporate/admin subnet(s))"
#   type        = list(string)
#   default     = ["10.0.0.0/8"] # CHANGE to your actual trusted subnet(s)
# }