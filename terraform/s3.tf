# Create S3 bucket with a specific prefix
resource "aws_s3_bucket" "fitbit-bucket" {
  bucket_prefix = var.S3_BUCKET_PREFIX
  force_destroy = true
}

# Enable versioning for S3 bucket
resource "aws_s3_bucket_versioning" "fitbit-bucket-versioning" {
  bucket = aws_s3_bucket.fitbit-bucket.id
  versioning_configuration {
    status = var.S3_VERSIONING
  }
}
