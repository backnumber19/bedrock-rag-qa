variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "aws_profile" {
  description = "AWS CLI profile name"
  type        = string
  default     = "default"
}

variable "project_name" {
  description = "Project name used for resource naming"
  type        = string
  default     = "bedrock-rag-qa-v2-west"
}

variable "environment" {
  description = "Environment (dev, staging, production)"
  type        = string
  default     = "production"
}

variable "embedding_model_id" {
  description = "Bedrock embedding model ID"
  type        = string
  default     = "amazon.titan-embed-text-v1"
}

variable "llm_model_id" {
  description = "Bedrock LLM model ID"
  type        = string
  default     = "anthropic.claude-3-haiku-20240307-v1:0"
}

variable "s3_bucket_name" {
  description = "S3 bucket name for documents"
  type        = string
  default     = ""  # Will be generated if empty
}

variable "opensearch_collection_name" {
  description = "OpenSearch Serverless collection name"
  type        = string
  default     = ""  # Will be generated if empty
}

variable "knowledge_base_name" {
  description = "Bedrock Knowledge Base name"
  type        = string
  default     = ""  # Will be generated if empty
}

# Local variables for dynamic naming
locals {
  s3_bucket_name              = var.s3_bucket_name != "" ? var.s3_bucket_name : "${var.project_name}-documents-${data.aws_caller_identity.current.account_id}"
  opensearch_collection_name  = var.opensearch_collection_name != "" ? var.opensearch_collection_name : "${var.project_name}-vectors"
  knowledge_base_name         = var.knowledge_base_name != "" ? var.knowledge_base_name : "${var.project_name}-kb"
  
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}