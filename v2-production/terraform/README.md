# Terraform Infrastructure for bedrock-rag-qa-v2

This directory contains Infrastructure as Code (IaC) for deploying the production-ready RAG system on AWS.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Files Structure](#files-structure)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Resources Created](#resources-created)
- [Variables](#variables)
- [Outputs](#outputs)
- [Cost Estimation](#cost-estimation)

---

## 🎯 Overview

This Terraform configuration deploys a complete AWS infrastructure for a production-grade RAG (Retrieval-Augmented Generation) system, including:

- S3 storage with versioning and lifecycle policies
- OpenSearch Serverless for vector search
- AWS Bedrock Knowledge Base
- CloudWatch monitoring and alerting
- IAM roles and policies

**Deployment Time**: ~10-15 minutes  
**Estimated Cost**: ~$5-8/month (100 queries/day)

---

## 🏗️ Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                    AWS Infrastructure                       │
└─────────────────────────────────────────────────────────────┘

PDF Files (Local)
    ↓ (upload)
┌──────────────────┐
│  S3 Bucket       │ ← Versioning + Lifecycle
│  (documents)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Bedrock Knowledge Base              │
│  - Auto PDF parsing                  │
│  - Chunking (300 tokens, 20% overlap)│
│  - Titan Embeddings v1               │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  OpenSearch Serverless               │
│  - Vector search (1536-dim)          │
│  - Auto-scaling                      │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Claude 3 Haiku                      │
│  - Answer generation                 │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  CloudWatch                          │
│  - Logs + Metrics + Dashboard        │
└──────────────────────────────────────┘
```

---

## 📁 Files Structure

| File | Purpose | Key Resources |
|------|---------|---------------|
| **main.tf** | Provider & basic setup | AWS provider, account info |
| **variable.tf** | Variable definitions | Region, model IDs, naming |
| **s3.tf** | Document storage | S3 bucket, versioning, lifecycle |
| **iam.tf** | Access control | IAM roles, policies |
| **opensearch.tf** | Vector database | OpenSearch Serverless, policies |
| **kb.tf** | Knowledge Base | Bedrock KB, data source, chunking |
| **cloudwatch.tf** | Monitoring | Log groups, dashboard, alarms |
| **outputs.tf** | Output values | IDs, ARNs, endpoints |

---

## ✅ Prerequisites

### 1. Install Terraform

```bash
# macOS (Homebrew)
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Verify installation
terraform --version
# Output: Terraform v1.x.x
```
### 2. AWS CLI Configuration

```bash
# Configure AWS credentials
aws configure

# Verify access
aws sts get-caller-identity
```

### 3. IAM Permissions Setup

⚠️ **Critical**: Your AWS user needs specific permissions to create infrastructure.

#### Required Managed Policies (6)

Attach these policies to your IAM user (e.g., `bedrock-user`):

```bash
# Method 1: AWS Console
# IAM → Users → [your-user] → Add permissions → Attach policies directly

# Method 2: AWS CLI (if you have admin access)
USER_NAME="bedrock-user"  # Replace with your username

aws iam attach-user-policy --user-name $USER_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam attach-user-policy --user-name $USER_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonOpenSearchServiceFullAccess

aws iam attach-user-policy --user-name $USER_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

aws iam attach-user-policy --user-name $USER_NAME \
  --policy-arn arn:aws:iam::aws:policy/AmazonSageMakerFullAccess

aws iam attach-user-policy --user-name $USER_NAME \
  --policy-arn arn:aws:iam::aws:policy/CloudWatchFullAccess

aws iam attach-user-policy --user-name $USER_NAME \
  --policy-arn arn:aws:iam::aws:policy/IAMFullAccess
```

#### Required Inline Policy (1)

OpenSearch Serverless requires additional permissions not included in managed policies:

```bash
# Create inline policy for OpenSearch Serverless
aws iam put-user-policy \
  --user-name $USER_NAME \
  --policy-name OpenSearchServerlessFullAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "aoss:*",
        "Resource": "*"
      }
    ]
  }'
```

#### Verify All Permissions

```bash
# Check managed policies
aws iam list-attached-user-policies --user-name $USER_NAME

# Check inline policies
aws iam list-user-policies --user-name $USER_NAME
```

**Expected Output:**
```json
// Managed Policies (6)
{
    "AttachedPolicies": [
        {"PolicyName": "AmazonBedrockFullAccess"},
        {"PolicyName": "AmazonOpenSearchServiceFullAccess"},
        {"PolicyName": "AmazonS3FullAccess"},
        {"PolicyName": "AmazonSageMakerFullAccess"},
        {"PolicyName": "CloudWatchFullAccess"},
        {"PolicyName": "IAMFullAccess"}
    ]
}

// Inline Policies (1)
{
    "PolicyNames": [
        "OpenSearchServerlessFullAccess"
    ]
}
```

#### Alternative: AdministratorAccess (Personal Accounts Only)

For personal AWS accounts (not production):

```bash
aws iam attach-user-policy \
  --user-name $USER_NAME \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

⚠️ **Warning**: `AdministratorAccess` grants full access to all AWS services. Only use for personal learning/development accounts.

---

### 4. Bedrock Model Access

⚠️ **Important**: Request model access in AWS Console before running Terraform!

1. Go to: https://console.aws.amazon.com/bedrock/
2. Navigate to: **Model access**
3. Click: **Request access**
4. Select models:
   - ✅ Claude 3 Haiku (or Claude 3.5 Sonnet)
   - ✅ Titan Embeddings G1 - Text v1
5. Submit request (usually instant approval)

---

## 🚀 Quick Start

### Step 1: Initialize Terraform

```bash
cd /Users/f2407ln0001/Desktop/lim/bedrock-rag-qa/v2-production/terraform

terraform init
```

**Output:**
```text
Initializing the backend...
Initializing provider plugins...
Finding hashicorp/aws versions matching "~> 5.0"...
Installing hashicorp/aws v5.x.x...
Terraform has been successfully initialized!
```


### Step 2: Preview Changes

```bash
terraform plan
```

**Expected Output:**
```text
Plan: 21 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + cloudwatch_dashboard_name      = "bedrock-rag-qa-v2-dashboard"
  + cloudwatch_log_group_name      = "/aws/bedrock-rag-qa-v2/application"
  + data_source_id                 = (known after apply)
  + knowledge_base_arn             = (known after apply)
  + knowledge_base_id              = (known after apply)
  + opensearch_collection_arn      = (known after apply)
  + opensearch_collection_endpoint = (known after apply)
  + s3_bucket_arn                  = (known after apply)
  + s3_bucket_name                 = (known after apply)
  + setup_summary                  = {
      + data_source_id      = (known after apply)
      + knowledge_base_id   = (known after apply)
      + opensearch_endpoint = (known after apply)
      + region              = "us-east-1"
      + s3_bucket           = (known after apply)
    }
```


### Step 3: Apply Configuration

```bash
terraform apply

# Review the plan and type: yes
```

**Deployment Progress** (~10-15 minutes):
```text
✅ Creating IAM roles...
✅ Creating S3 bucket...
✅ Creating OpenSearch encryption policy...
✅ Creating OpenSearch network policy...
✅ Creating OpenSearch access policy...
✅ Creating OpenSearch collection... (this takes 5-10 mins)
✅ Creating Bedrock Knowledge Base...
✅ Creating data source...
✅ Creating CloudWatch resources...
Apply complete! Resources: 21 added, 0 changed, 0 destroyed.
Outputs:
knowledge_base_id = "kb-xxxxxxxxxxxx" ⬅️ COPY THIS!
data_source_id = "ds-xxxxxxxxxxxx"
s3_bucket_name = "bedrock-rag-qa-v2-documents-123456789012"
```


### Step 4: Save Important Values

```bash
# Save outputs to file
terraform output > outputs.txt

# Or get specific value
terraform output knowledge_base_id
# Output: kb-xxxxxxxxxxxx
```

---

## 📦 Resources Created

### Total: 21 AWS Resources

| Category | Count | Resources |
|----------|-------|-----------|
| **S3** | 6 | Bucket, versioning, encryption, public block, lifecycle, policy |
| **IAM** | 4 | Role, S3 policy, Bedrock policy, OpenSearch policy |
| **OpenSearch** | 4 | Encryption policy, network policy, access policy, collection |
| **Bedrock** | 2 | Knowledge Base, data source |
| **CloudWatch** | 5 | App logs, KB logs, dashboard, SNS topic, alarm |

### Resource Details

#### 1. S3 Storage (s3.tf)

| Resource | Configuration |
|----------|---------------|
| **Bucket** | Auto-generated name with account ID |
| **Versioning** | Enabled |
| **Encryption** | AES256 |
| **Public Access** | Blocked (all 4 settings) |
| **Lifecycle** | 30d → IA, 90d → Glacier, 180d → Delete |

#### 2. IAM Roles (iam.tf)

| Role | Permissions |
|------|-------------|
| **bedrock-kb-role** | - S3: GetObject, ListBucket<br>- Bedrock: InvokeModel<br>- OpenSearch: APIAccessAll |

#### 3. OpenSearch Serverless (opensearch.tf)

| Component | Setting |
|-----------|---------|
| **Type** | VECTORSEARCH |
| **Encryption** | AWS owned key |
| **Network** | Public access |
| **Access** | Bedrock KB + your account |

#### 4. Bedrock Knowledge Base (kb.tf)

| Setting | Value |
|---------|-------|
| **Embedding Model** | amazon.titan-embed-text-v1 |
| **Vector Dimension** | 1,536 |
| **Chunking Strategy** | FIXED_SIZE |
| **Max Tokens** | 300 |
| **Overlap** | 20% |

#### 5. CloudWatch Monitoring (cloudwatch.tf)

| Resource | Retention | Purpose |
|----------|-----------|---------|
| **App Logs** | 30 days | Application logs |
| **KB Logs** | 14 days | Knowledge Base logs |
| **Dashboard** | - | Metrics visualization |
| **Alarm** | - | Error rate > 10 |

---

## 🔧 Variables

### Configurable Variables

Edit `variable.tf` or create `terraform.tfvars`:

```hcl
# terraform.tfvars (optional)
aws_region      = "us-east-1"
aws_profile     = "default"
project_name    = "bedrock-rag-qa-v2"
environment     = "production"

# Model configurations
embedding_model_id = "amazon.titan-embed-text-v1"
llm_model_id      = "anthropic.claude-3-haiku-20240307-v1:0"

# Or use Claude 3.5 Sonnet
# llm_model_id = "anthropic.claude-3-5-sonnet-20240620-v1:0"
```

### Available Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `aws_region` | `us-east-1` | AWS region for resources |
| `aws_profile` | `default` | AWS CLI profile name |
| `project_name` | `bedrock-rag-qa-v2` | Project name (used in resource naming) |
| `environment` | `production` | Environment tag |
| `embedding_model_id` | `amazon.titan-embed-text-v1` | Bedrock embedding model |
| `llm_model_id` | `anthropic.claude-3-haiku-20240307-v1:0` | Bedrock LLM model |

---

## 📤 Outputs

After successful deployment, you'll get these output values:

| Output | Usage |
|--------|-------|
| `knowledge_base_id` | **Required for Python code** - KB ID for queries |
| `data_source_id` | **Required for sync** - Trigger KB data ingestion |
| `s3_bucket_name` | **Required for upload** - Upload PDFs here |
| `opensearch_collection_endpoint` | OpenSearch API endpoint |
| `cloudwatch_log_group_name` | Log group for Python logging |
| `cloudwatch_dashboard_name` | Dashboard name in AWS Console |

### Usage Example

```python
# src/config.py
KNOWLEDGE_BASE_ID = "kb-xxxxxxxxxxxx"  # From terraform output
DATA_SOURCE_ID = "ds-xxxxxxxxxxxx"     # From terraform output
S3_BUCKET = "bedrock-rag-qa-v2-documents-123456789012"  # From terraform output
```

---

## 💰 Cost Estimation

### Monthly Cost Breakdown (100 queries/day)

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| **S3 Standard** | 10GB | $0.23 |
| **S3 IA** (old versions) | 5GB | $0.06 |
| **OpenSearch Serverless** | 2 OCU | $2-4 |
| **Bedrock KB Storage** | Vector index | $0.50 |
| **Bedrock Embeddings** | 3K queries | $0.30 |
| **Bedrock LLM (Haiku)** | 3K queries | $1.50 |
| **CloudWatch Logs** | 10GB | $0.50 |
| **CloudWatch Alarms** | 1 alarm | $0.10 |
| **Total** | | **~$5-8** |

---

## 🐛 Troubleshooting

### Error: "Access Denied" or "Insufficient Permissions"

**Symptom:**
```text
Error: User is not authorized to perform: iam:CreateRole
Error: User is not authorized to perform: aoss:CreateSecurityPolicy
```

**Solution 1**: Add all required permissions (Recommended)

```bash
USER_NAME="bedrock-user"

# Add 6 managed policies
for policy in \
  "AmazonBedrockFullAccess" \
  "AmazonOpenSearchServiceFullAccess" \
  "AmazonS3FullAccess" \
  "AmazonSageMakerFullAccess" \
  "CloudWatchFullAccess" \
  "IAMFullAccess"
do
  aws iam attach-user-policy \
    --user-name $USER_NAME \
    --policy-arn arn:aws:iam::aws:policy/$policy
  echo "✅ Added $policy"
done

# Add OpenSearch Serverless inline policy
aws iam put-user-policy \
  --user-name $USER_NAME \
  --policy-name OpenSearchServerlessFullAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "aoss:*", "Resource": "*"}]
  }'
echo "✅ Added OpenSearchServerlessFullAccess"
```

**Solution 2**: Use AdministratorAccess (Personal accounts only)

```bash
aws iam attach-user-policy \
  --user-name bedrock-user \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

**Verify permissions:**
```bash
aws iam list-attached-user-policies --user-name bedrock-user
aws iam list-user-policies --user-name bedrock-user
```

### Error: "aoss:CreateSecurityPolicy" permission denied

**Solution**: This means OpenSearch Serverless inline policy is missing.

```bash
aws iam put-user-policy \
  --user-name bedrock-user \
  --policy-name OpenSearchServerlessFullAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [{"Effect": "Allow", "Action": "aoss:*", "Resource": "*"}]
  }'
```

### Error: "No module named 'dotenv'"

This is a Python issue, not Terraform. See main project README.

### Error: "Access Denied" or "Insufficient Permissions"

**Solution**: Check your IAM permissions. Required policies:
- `AmazonBedrockFullAccess`
- `AmazonS3FullAccess`
- `AmazonOpenSearchServiceFullAccess`
- `CloudWatchFullAccess`

### Error: "Model access not granted"

**Solution**: Request model access in Bedrock Console (see Prerequisites)

### Error: "OpenSearch collection creation timeout"

**Solution**: Wait 10-15 minutes. OpenSearch Serverless takes time to provision.

### Error: "no such index [bedrock-knowledge-base-default-index]"

**Symptom:**
```text
Error: creating Bedrock Agent Knowledge Base
ValidationException: The knowledge base storage configuration provided is invalid... 
Dependency error document status code: 404, error message: no such index 
[bedrock-knowledge-base-default-index]
```

**Root Cause:**  
Bedrock Knowledge Base expects the OpenSearch index to exist before creation, but OpenSearch Serverless doesn't automatically create indexes. This is a known issue with AWS Bedrock + OpenSearch Serverless integration.

**Solution 1: Manual Index Creation (Recommended)**

```bash
# 1. Install required Python libraries
pip install opensearch-py boto3 requests-aws4auth

# 2. Get your OpenSearch endpoint
terraform output opensearch_collection_endpoint
# Output: https://xxxxx.us-west-2.aoss.amazonaws.com

# 3. Create index using Python script
python3 << 'EOF'
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection, AWSV4SignerAuth

# Replace with your actual endpoint (without https://)
host = 'gw2qu42cb1cs6z9agqe4.us-west-2.aoss.amazonaws.com'
region = 'us-west-2'

credentials = boto3.Session().get_credentials()
auth = AWSV4SignerAuth(credentials, region, 'aoss')

client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

index_name = 'bedrock-knowledge-base-default-index'
index_body = {
    'settings': {'index.knn': True},
    'mappings': {
        'properties': {
            'bedrock-knowledge-base-default-vector': {
                'type': 'knn_vector',
                'dimension': 1536,
                'method': {'name': 'hnsw', 'engine': 'faiss'}
            },
            'AMAZON_BEDROCK_TEXT_CHUNK': {'type': 'text'},
            'AMAZON_BEDROCK_METADATA': {'type': 'text'}
        }
    }
}

try:
    response = client.indices.create(index=index_name, body=index_body)
    print('✅ Index created successfully!')
except Exception as e:
    if 'resource_already_exists' in str(e).lower():
        print('✅ Index already exists')
    else:
        print(f'❌ Error: {e}')
        raise
EOF

# 4. Re-run Terraform
terraform apply
```

**Solution 2: Add Wait Time in Terraform**

Add a time sleep resource in `kb.tf`:

```hcl
# kb.tf - Add before knowledge base resource
resource "time_sleep" "wait_for_opensearch" {
  depends_on = [aws_opensearchserverless_collection.vectors]
  
  create_duration = "5m"  # Wait 5 minutes for OpenSearch to stabilize
}

resource "aws_bedrockagent_knowledge_base" "main" {
  # ... existing configuration ...
  
  depends_on = [
    time_sleep.wait_for_opensearch,  # Add this
    aws_opensearchserverless_access_policy.data_access,
    aws_iam_role_policy.bedrock_kb_opensearch
  ]
}
```

Then add time provider in `main.tf`:

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    time = {  # Add this
      source  = "hashicorp/time"
      version = "~> 0.9"
    }
  }
}
```

Run:
```bash
terraform init  # Install time provider
terraform apply
```

**Note:** Solution 1 (manual index creation) is more reliable as it directly addresses the root cause.

---

### Error: "OpenSearch Collection stuck in CREATING state for 1+ hour"

**Symptom:**
```text
aws_opensearchserverless_collection.vectors: Still creating... [01h00m00s elapsed]
Cannot delete: Collection cannot be deleted because it is not in 'ACTIVE' or 'FAILED' status
```

**Root Cause:**  
Regional capacity or service issues in `us-east-1`. OpenSearch Serverless typically creates in 3-10 minutes.

**Solution: Switch to us-west-2 region**

```hcl
# variable.tf
variable "aws_region" {
  default = "us-west-2"  # Change from us-east-1
}
```

```bash
# Clean up stuck resources in us-east-1 (optional)
aws opensearchserverless list-collections --region us-east-1

# If collection exists in us-east-1, wait or contact AWS Support

# Start fresh in us-west-2
rm -rf terraform.tfstate* .terraform .terraform.lock.hcl
terraform init
terraform apply
```