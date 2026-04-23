resource "aws_s3_bucket" "bronze" {
  bucket = "lakehouse-bronze"
}

resource "aws_s3_bucket" "silver" {
  bucket = "lakehouse-silver"
}

resource "aws_s3_bucket" "gold" {
  bucket = "lakehouse-gold"
}

resource "aws_s3_bucket_versioning" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "bronze" {
  bucket = aws_s3_bucket.bronze.id
  rule {
    id     = "expire-90d"
    status = "Enabled"
    filter {
      prefix = ""
    }
    expiration {
      days = 90
    }
  }
}
