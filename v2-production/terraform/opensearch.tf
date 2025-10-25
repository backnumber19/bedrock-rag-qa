# Encryption policy
resource "aws_opensearchserverless_security_policy" "encryption" {
  name = "${var.project_name}-encrypt"
  type = "encryption"
  
  policy = jsonencode({
    Rules = [
      {
        ResourceType = "collection"
        Resource = ["collection/${local.opensearch_collection_name}"]
      }
    ]
    AWSOwnedKey = true
  })
}

# Network policy
resource "aws_opensearchserverless_security_policy" "network" {
  name = "${var.project_name}-network"
  type = "network"
  
  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "collection"
          Resource = ["collection/${local.opensearch_collection_name}"]
        },
        {
          ResourceType = "dashboard"
          Resource = ["collection/${local.opensearch_collection_name}"]
        }
      ]
      AllowFromPublic = true
    }
  ])
}

# Data access policy
resource "aws_opensearchserverless_access_policy" "data_access" {
  name = "${var.project_name}-access"
  type = "data"
  
  policy = jsonencode([
    {
      Rules = [
        {
          ResourceType = "collection"
          Resource = ["collection/${local.opensearch_collection_name}"]
          Permission = [
            "aoss:CreateCollectionItems",
            "aoss:DeleteCollectionItems",
            "aoss:UpdateCollectionItems",
            "aoss:DescribeCollectionItems"
          ]
        },
        {
          ResourceType = "index"
          Resource = ["index/${local.opensearch_collection_name}/*"]
          Permission = [
            "aoss:CreateIndex",
            "aoss:DeleteIndex",
            "aoss:UpdateIndex",
            "aoss:DescribeIndex",
            "aoss:ReadDocument",
            "aoss:WriteDocument"
          ]
        }
      ]
      Principal = [
        aws_iam_role.bedrock_kb.arn,
        data.aws_caller_identity.current.arn
      ]
    }
  ])
}

# OpenSearch Serverless collection
resource "aws_opensearchserverless_collection" "vectors" {
  name = local.opensearch_collection_name
  type = "VECTORSEARCH"
  
  depends_on = [
    aws_opensearchserverless_security_policy.encryption,
    aws_opensearchserverless_security_policy.network
  ]
  
  tags = merge(
    local.common_tags,
    {
      Name = "RAG Vector Store"
    }
  )
}