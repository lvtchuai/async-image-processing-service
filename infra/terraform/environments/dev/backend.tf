terraform {
  backend "s3" {
    bucket         = "pixelpipe-tfstate-342996267691"
    key            = "dev/terraform.tfstate"
    region         = "ap-southeast-1"
    dynamodb_table = "pixelpipe-tf-locks"
    encrypt        = true
  }
}