data "aws_caller_identity" "current" {}

# --- Networking + cluster (tái dùng module ShortLink) ---
module "vpc" {
  source             = "../../modules/vpc"
  name               = var.cluster_name
  vpc_cidr           = var.vpc_cidr
  az_count           = 2
  single_nat_gateway = true
}

module "eks" {
  source          = "../../modules/eks"
  cluster_name    = var.cluster_name
  cluster_version = "1.31"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnet_ids
  tags            = { Project = "pixelpipe" }
}

# --- Managed services ---
module "ecr" {
  source = "../../modules/ecr"
  names  = ["pixelpipe-api", "pixelpipe-worker"]
}

module "s3" {
  source      = "../../modules/s3"
  bucket_name = "pixelpipe-images-${data.aws_caller_identity.current.account_id}"  # tên global-unique
}

module "rds" {
  source     = "../../modules/rds"
  identifier = "pixelpipe-db"
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
  vpc_cidr   = var.vpc_cidr
  password   = var.db_password
}

module "mq" {
  source      = "../../modules/mq"
  broker_name = "pixelpipe-mq"
  vpc_id      = module.vpc.vpc_id
  subnet_ids  = module.vpc.private_subnet_ids
  vpc_cidr    = var.vpc_cidr
  password    = var.mq_password
}

# IAM user cho app truy cập S3 (lab; production nên dùng IRSA - keyless)
resource "aws_iam_user" "app" {
  name          = "pixelpipe-app"
  force_destroy = true
}

resource "aws_iam_user_policy" "app_s3" {
  name = "s3-access"
  user = aws_iam_user.app.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject", "s3:PutObject", "s3:ListBucket"]
      Resource = [module.s3.bucket_arn, "${module.s3.bucket_arn}/*"]
    }]
  })
}

resource "aws_iam_access_key" "app" {
  user = aws_iam_user.app.name
}

output "s3_access_key" {
  value     = aws_iam_access_key.app.id
  sensitive = true
}

output "s3_secret_key" {
  value     = aws_iam_access_key.app.secret
  sensitive = true
}