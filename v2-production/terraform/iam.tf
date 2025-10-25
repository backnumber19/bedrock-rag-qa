# IAM role for Bedrock Knowledge Base
resource "aws_iam_role" "bedrock_kb" {
  name = "${var.project_name}-bedrock-kb-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "bedrock.amazonaws.com"
        }
        Action = "sts:AssumeRole"
        Condition = {
          StringEquals = {
            "aws:SourceAccount" = data.aws_caller_identity.current.account_id
          }
          ArnLike = {
            "aws:SourceArn" = "arn:aws:bedrock:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:knowledge-base/*"
          }
        }
      }
    ]
  })
  
  tags = local.common_tags
}

# Policy for S3 access
resource "aws_iam_role_policy" "bedrock_kb_s3" {
  name = "${var.project_name}-bedrock-kb-s3-policy"
  role = aws_iam_role.bedrock_kb.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.documents.arn,
          "${aws_s3_bucket.documents.arn}/*"
        ]
      }
    ]
  })
}

# Policy for Bedrock model access
resource "aws_iam_role_policy" "bedrock_kb_model" {
  name = "${var.project_name}-bedrock-kb-model-policy"
  role = aws_iam_role.bedrock_kb.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = [
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/${var.embedding_model_id}",
          "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/${var.llm_model_id}"
        ]
      }
    ]
  })
}

# Policy for OpenSearch Serverless access
resource "aws_iam_role_policy" "bedrock_kb_opensearch" {
  name = "${var.project_name}-bedrock-kb-opensearch-policy"
  role = aws_iam_role.bedrock_kb.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "aoss:APIAccessAll"
        ]
        Resource = [
          aws_opensearchserverless_collection.vectors.arn
        ]
      }
    ]
  })
}