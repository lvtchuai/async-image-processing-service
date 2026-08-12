provider "aws" {
  region = var.region
  default_tags {
    tags = { Project = "pixelpipe", ManagedBy = "terraform", Env = "dev" }
  }
}