resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted IPs"
  vpc_id      = var.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = var.allowed_ssh_cidr  # Restrict SSH to trusted network(s)
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = var.allowed_egress_cidr  # (Recommended: restrict this as needed)
  }
}