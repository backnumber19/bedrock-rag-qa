resource "time_sleep" "wait_for_opensearch" {
  depends_on = [aws_opensearchserverless_collection.vectors]
  
  create_duration = "1m"
}

# Bedrock Knowledge Base
resource "aws_bedrockagent_knowledge_base" "main" {
  name     = local.knowledge_base_name
  role_arn = aws_iam_role.bedrock_kb.arn
  
  knowledge_base_configuration {
    vector_knowledge_base_configuration {
      embedding_model_arn = "arn:aws:bedrock:${data.aws_region.current.name}::foundation-model/${var.embedding_model_id}"
    }
    type = "VECTOR"
  }
  
  storage_configuration {
    type = "OPENSEARCH_SERVERLESS"
    
    opensearch_serverless_configuration {
      collection_arn    = aws_opensearchserverless_collection.vectors.arn
      vector_index_name = "bedrock-knowledge-base-default-index"
      
      field_mapping {
        vector_field   = "bedrock-knowledge-base-default-vector"
        text_field     = "AMAZON_BEDROCK_TEXT_CHUNK"
        metadata_field = "AMAZON_BEDROCK_METADATA"
      }
    }
  }
  
  depends_on = [
    time_sleep.wait_for_opensearch,
    aws_opensearchserverless_collection.vectors,
    aws_opensearchserverless_access_policy.data_access,
    aws_iam_role_policy.bedrock_kb_opensearch
  ]
  
  tags = merge(
    local.common_tags,
    {
      Name = "RAG Knowledge Base"
    }
  )
}

# S3 Data Source
resource "aws_bedrockagent_data_source" "s3_documents" {
  knowledge_base_id = aws_bedrockagent_knowledge_base.main.id
  name              = "s3-documents"
  
  data_source_configuration {
    type = "S3"
    
    s3_configuration {
      bucket_arn = aws_s3_bucket.documents.arn
      
      # Optional: specify inclusion prefixes
      # inclusion_prefixes = ["documents/"]
    }
  }
  
  # Chunking strategy
  vector_ingestion_configuration {
    chunking_configuration {
      chunking_strategy = "FIXED_SIZE"
      
      fixed_size_chunking_configuration {
        max_tokens         = 300
        overlap_percentage = 20
      }
    }
  }
  
  depends_on = [
    aws_bedrockagent_knowledge_base.main,
    aws_s3_bucket_policy.documents
  ]
}