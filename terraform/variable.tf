variable "AWS_REGION" {
  description = "Region for the AWS services to run in"
  type        = string
}

variable "AWS_BILLING_EMAIL" {
  description = "Billing email for AWS budget"
  type        = string
}

variable "S3_BUCKET_PREFIX" {
  description = "The prefix of the bucket used in S3. Must be unique"
  type        = string
}

variable "S3_VERSIONING" {
  description = "Enable or disable versioning for S3 bucket"
  type        = string
  default     = "Disabled"
}

variable "REDSHIFT_ADMIN_USER" {
  description = "Username for the database in the RDS cluster"
  type        = string
}

variable "REDSHIFT_PW" {
  description = "Password for the database in the RDS cluster"
  type        = string
}

variable "REDSHIFT_DATABASE_NAME" {
  description = "Name of the redshift db used to store data"
  type        = string
}