variable "broker_name" {
  type        = string
  description = "Name identifier for MQ broker"
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC where the MQ broker will be deployed"
}

variable "subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs where the MQ broker will be deployed"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block of the VPC"
}

variable "username" {
  type        = string
  description = "Username for the MQ broker user"
  default     = "pixel"
}

variable "password" {
  type        = string
  description = "Password for the MQ broker user"
  sensitive   = true
} # >= 12 characters, no commas