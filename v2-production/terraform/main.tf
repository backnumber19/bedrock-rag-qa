terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
  
  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = "bedrock-rag-qa"
    }
  }
}

# Data source: Current AWS account
data "aws_caller_identity" "current" {}

# Data source: Current AWS region
data "aws_region" "current" {}