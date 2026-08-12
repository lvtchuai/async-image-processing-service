variable "names" {
  description = "List of ECR repository names to create"
  type        = list(string)
} # ["pixelpipe-api","pixelpipe-worker"]