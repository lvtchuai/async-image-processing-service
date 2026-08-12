variable "name" {
  description = "Prefix name for the VPC and its resources"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
}

variable "az_count" {
  description = "Number of Availability Zones to use"
  type        = number
  default     = 2
}

variable "single_nat_gateway" {
  description = "true if you want to create a single NAT Gateway for the VPC, false for one per AZ"
  type        = bool
  default     = true
}
