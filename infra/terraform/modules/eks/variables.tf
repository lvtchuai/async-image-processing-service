variable "cluster_name" {
  description = "Tên EKS cluster"
  type        = string
}

variable "cluster_version" {
  description = "Phiên bản Kubernetes"
  type        = string
  default     = "1.31"
}

variable "vpc_id" {
  description = "VPC đặt cluster vào"
  type        = string
}

variable "subnet_ids" {
  description = "Private subnet cho node group"
  type        = list(string)
}

variable "instance_types" {
  description = "Loại EC2 cho node"
  type        = list(string)
  default     = ["t3.small"]
}

variable "min_size" {
  type    = number
  default = 2
}

variable "max_size" {
  type    = number
  default = 3
}

variable "desired_size" {
  type    = number
  default = 2
}

variable "tags" {
  type    = map(string)
  default = {}
}