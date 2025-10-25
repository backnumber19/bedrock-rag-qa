# CloudWatch Log Group for application logs
resource "aws_cloudwatch_log_group" "app_logs" {
  name              = "/aws/${var.project_name}/application"
  retention_in_days = 30
  
  tags = merge(
    local.common_tags,
    {
      Name = "Application Logs"
    }
  )
}

# CloudWatch Log Group for Knowledge Base
resource "aws_cloudwatch_log_group" "kb_logs" {
  name              = "/aws/bedrock/${var.project_name}/knowledge-base"
  retention_in_days = 14
  
  tags = merge(
    local.common_tags,
    {
      Name = "Knowledge Base Logs"
    }
  )
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Bedrock", "Invocations", { stat = "Sum", label = "API Calls" }]
          ]
          period = 300
          stat   = "Sum"
          region = data.aws_region.current.name
          title  = "Bedrock API Invocations"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/S3", "NumberOfObjects", { stat = "Average" }]
          ]
          period = 86400
          stat   = "Average"
          region = data.aws_region.current.name
          title  = "S3 Documents Count"
        }
      },
      {
        type = "log"
        properties = {
          query   = "SOURCE '${aws_cloudwatch_log_group.app_logs.name}' | fields @timestamp, @message | sort @timestamp desc | limit 20"
          region  = data.aws_region.current.name
          title   = "Recent Application Logs"
        }
      }
    ]
  })
}

# SNS Topic for alerts (optional)
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts"
  
  tags = merge(
    local.common_tags,
    {
      Name = "Alert Notifications"
    }
  )
}

# CloudWatch Alarm for high error rate (example)
resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.project_name}-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Bedrock"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "This metric monitors Bedrock error rate"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  tags = local.common_tags
}