## 🎯 Project Evolution

### v1-prototype: RAG System Foundation

**Purpose**: Proof of concept and local prototype for RAG system

**Key Technologies**:
- AWS Bedrock (Claude 3 Haiku, Titan Embeddings)
- LangChain
- FAISS (Local vector store)
- Python

**Features**:
- ✅ Rapid prototyping
- ✅ Local development environment
- ✅ Cost-efficient (~$0.60/month)
- ⚠️ Manual data management
- ⚠️ Limited scalability

[📖 View v1 documentation →](./v1-prototype/README.md)

---

### v2-production: Production-Grade System

**Purpose**: Enterprise-ready system with automated infrastructure and monitoring

**Key Technologies**:
- AWS Bedrock Knowledge Base
- Amazon OpenSearch Serverless
- S3 auto-sync
- CloudWatch monitoring
- Terraform (IaC)

**Features**:
- ✅ Automated data pipeline
- ✅ Serverless scalability
- ✅ Operational monitoring
- ✅ Infrastructure as Code
- ⚠️ Higher cost (~$5-10/month)

[📖 View v2 documentation →](./v2-production/README.md)

---

## 🎓 Learning Outcomes

### What I Built in v1
- RAG pipeline implementation
- LangChain integration
- Vector embeddings & search
- Prompt engineering

### What I Built in v2
- Cloud-native architecture
- MLOps/DevOps practices
- Operational monitoring
- Infrastructure as Code

---

## 📊 Comparison

| Feature | v1-prototype | v2-production |
|---------|-------------|---------------|
| **Vector Store** | Local FAISS | OpenSearch Serverless |
| **Data Management** | Manual | S3 auto-sync |
| **Knowledge Base** | Custom | AWS Bedrock KB |
| **Monitoring** | None | CloudWatch |
| **Infrastructure** | Manual | Terraform IaC |
| **Scalability** | Single machine | Auto-scaling |
| **Cost** | ~$0.60/month | ~$5-10/month |

---

## 🚀 Quick Start

### v1-prototype
```bash
cd v1-prototype
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# View v1-prototype/README.md for details
```

### v2-production
```bash
cd v2-production
# View v2-production/README.md for setup guide
```
