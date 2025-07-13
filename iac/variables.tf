variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

# Optional: Allow override of default topic
variable "sns_topic_arn" {
  description = "Custom SNS topic ARN if pre-created"
  type        = string
  default     = ""
}

variable "schedule_expression" {
  type    = string
  default = "cron(0 0 * * ? *)" # Midnight UTC daily
}
variable "alert_email" {
  default = ""
  type    = string
}