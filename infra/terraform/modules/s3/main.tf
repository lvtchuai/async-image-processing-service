# create s3 bucket
resource "aws_s3_bucket" "this" {
  bucket        = var.bucket_name
  force_destroy = true # cho destroy dù còn object (lab)
}

# block bucket không cho biến s3 thành public storage
resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# CORS (cross-origin resource sharing): cho browser GET object qua presigned URL (luồng verify presigned từ browser)
resource "aws_s3_bucket_cors_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  cors_rule {
    allowed_methods = ["GET"]
    allowed_origins = ["*"]
    allowed_headers = ["*"]
  }
}

