provider "aws" {
  region = var.aws_region
}

# --- IAM Role for Lambda ---
resource "aws_iam_role" "lambda_exec_role" {
  name               = "cost-analyzer-role"
  assume_role_policy = file("${path.module}/policy/trust-relationship.json")
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "cost-analyzer-policy"
  policy = file("${path.module}/policy/cost-analyzer-policy.json")
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# --- # SNS Topic # --- #
resource "aws_sns_topic" "cost_alert_topic" {
  name = "cost-analyzer-alerts"
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.cost_alert_topic.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# --- # Lambda Function # --- #
resource "aws_lambda_function" "cost_analyzer" {
  function_name = "cost-analyzer"
  runtime       = "python3.13"
  handler       = "lambda_function.lambda_handler"
  role          = aws_iam_role.lambda_exec_role.arn

  filename         = "${path.module}/packages/cost_analyzer.zip"
  source_code_hash = filebase64sha256("${path.module}/packages/cost_analyzer.zip")

  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.cost_alert_topic.arn
    }
  }

  depends_on = [aws_iam_role_policy_attachment.lambda_policy_attach]
}

# --- # Lambda Invocation via EventBridge # --- #
resource "aws_cloudwatch_event_rule" "daily_trigger" {
  name                = "daily-cost-analyzer-trigger"
  schedule_expression = var.schedule_expression
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.daily_trigger.name
  target_id = "costAnalyzerLambda"
  arn       = aws_lambda_function.cost_analyzer.arn
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.cost_analyzer.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.daily_trigger.arn
}
