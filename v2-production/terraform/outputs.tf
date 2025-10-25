output "s3_bucket_name" {
  description = "S3 bucket name for documents"
  value       = aws_s3_bucket.documents.id
}

output "s3_bucket_arn" {
  description = "S3 bucket ARN"
  value       = aws_s3_bucket.documents.arn
}

output "opensearch_collection_arn" {
  description = "OpenSearch Serverless collection ARN"
  value       = aws_opensearchserverless_collection.vectors.arn
}

output "opensearch_collection_endpoint" {
  description = "OpenSearch Serverless collection endpoint"
  value       = aws_opensearchserverless_collection.vectors.collection_endpoint
}

output "knowledge_base_id" {
  description = "Bedrock Knowledge Base ID"
  value       = aws_bedrockagent_knowledge_base.main.id
}

output "knowledge_base_arn" {
  description = "Bedrock Knowledge Base ARN"
  value       = aws_bedrockagent_knowledge_base.main.arn
}

output "data_source_id" {
  description = "S3 Data Source ID"
  value       = aws_bedrockagent_data_source.s3_documents.data_source_id
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch Log Group name"
  value       = aws_cloudwatch_log_group.app_logs.name
}

output "cloudwatch_dashboard_name" {
  description = "CloudWatch Dashboard name"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

# Summary output
output "setup_summary" {
  description = "Summary of created resources"
  value = {
    s3_bucket           = aws_s3_bucket.documents.id
    knowledge_base_id   = aws_bedrockagent_knowledge_base.main.id
    data_source_id      = aws_bedrockagent_data_source.s3_documents.data_source_id
    opensearch_endpoint = aws_opensearchserverless_collection.vectors.collection_endpoint
    region              = data.aws_region.current.name
  }
}