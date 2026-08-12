variable "identifier" {
  type        = string
  description = "Name identifier for RDS instance"
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC where the RDS instance will be deployed"
}

variable "subnet_ids" {
  type        = list(string)
  description = "List of subnet IDs where the RDS instance will be deployed"
} # private subnets

variable "vpc_cidr" {
  type        = string
  description = "CIDR block of the VPC"
}

# database credentials
variable "db_name" {
  type        = string
  description = "Name of the database to create"
  default     = "pixelpipe"
}

variable "username" {
  type        = string
  description = "Username for the database user"
  default     = "pixel"
}

variable "password" {
  type        = string
  description = "Password for the database user"
  sensitive   = true # restrict sensitive data from being displayed in logs or state files
}