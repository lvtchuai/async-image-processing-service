variable "region" {
    description = "AWS region to deploy resources"
  type    = string
  default = "ap-southeast-1"
}
variable "cluster_name" {
    description = "Name of the EKS cluster"
  type    = string
  default = "pixelpipe-eks"
}
variable "vpc_cidr" {
    description = "VPC CIDR block"
  type    = string
  default = "10.0.0.0/16"
}

variable "db_password" {
    description = "Password for the database"
  type      = string
  sensitive = true
} 

variable "mq_password" {
    description = "Password for the message queue"
  type      = string
  sensitive = true
}