variable "trusted_ssh_cidr_blocks" {
  description = "List of trusted IPv4/IPv6 CIDR blocks allowed to SSH (port 22). Do NOT use 0.0.0.0/0 or ::/0."
  type        = list(string)
  default     = []

  validation {
    condition = length([
      for cidr in var.trusted_ssh_cidr_blocks : cidr
      if (
        # Disallow 0.0.0.0/0 (full IPv4 Internet)
        cidr == "0.0.0.0/0"
        # Disallow ::/0 (full IPv6 Internet)
        || cidr == "::/0"
        # Disallow overly broad IPv4 CIDRs (e.g., anything broader than /24)
        || (can(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/([0-9]{1,2})$", cidr)) && (
            tonumber(regex("^([0-9]{1,3}\\.){3}[0-9]{1,3}/([0-9]{1,2})$", cidr)[1]) < 24
          ))
        # Disallow overly broad IPv6 CIDRs (e.g., anything broader than /64)
        || (can(regex("^([a-fA-F0-9:]+)/([0-9]{1,3})$", cidr)) && (
            tonumber(regex("^([a-fA-F0-9:]+)/([0-9]{1,3})$", cidr)[1]) < 64
          ))
      )
    ]) == 0
    error_message = "trusted_ssh_cidr_blocks cannot contain 0.0.0.0/0, ::/0, or overly broad CIDRs. Specify only trusted/specific IPs or ranges, e.g. ['203.0.113.18/32', '2001:db8::1/128', '192.0.2.0/24']."
  }
}

resource "aws_security_group" "ssh_open" {
  name        = "open_ssh"
  description = "Allow SSH from trusted sources"
  vpc_id      = var.vpc_id

  dynamic "ingress" {
    for_each = length(var.trusted_ssh_cidr_blocks) > 0 ? var.trusted_ssh_cidr_blocks : []
    content {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = can(regex(":", ingress.value)) ? [] : [ingress.value]
      ipv6_cidr_blocks = can(regex(":", ingress.value)) ? [ingress.value] : []
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}