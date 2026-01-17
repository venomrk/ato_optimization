# Deployment Guide

## Local Development

### Prerequisites
- Python 3.11+
- Docker & Docker Compose (optional, for full stack)
- API keys for at least one LLM provider

### Setup

1. **Install Python dependencies**
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Run locally**
```bash
# With Docker (recommended)
docker-compose up -d

# Or without Docker
python main.py
```

## Production Deployment

### Docker Deployment

**Build image:**
```bash
docker build -t research-platform:1.0.0 .
```

**Run with external PostgreSQL and Redis:**
```bash
docker run -d \
  --name research-platform \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@db-host:5432/research" \
  -e REDIS_URL="redis://redis-host:6379/0" \
  -e OPENAI_API_KEY="sk-xxx" \
  -e ANTHROPIC_API_KEY="sk-ant-xxx" \
  -v /data/papers:/app/data/papers \
  research-platform:1.0.0
```

### AWS Deployment

#### ECS/Fargate

1. **Push image to ECR:**
```bash
aws ecr create-repository --repository-name research-platform
$(aws ecr get-login --no-include-email)
docker tag research-platform:1.0.0 123456789.dkr.ecr.us-east-1.amazonaws.com/research-platform:1.0.0
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/research-platform:1.0.0
```

2. **Create RDS PostgreSQL instance:**
```bash
aws rds create-db-instance \
  --db-instance-identifier research-platform-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --master-user-password <password> \
  --allocated-storage 50
```

3. **Create ElastiCache Redis:**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id research-platform-cache \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

4. **Create ECS Task Definition:**
```json
{
  "family": "research-platform",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "2048",
  "memory": "4096",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "123456789.dkr.ecr.us-east-1.amazonaws.com/research-platform:1.0.0",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ],
      "secrets": [
        {"name": "OPENAI_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/research-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

5. **Create ECS Service with ALB:**
```bash
aws ecs create-service \
  --cluster research-cluster \
  --service-name research-platform \
  --task-definition research-platform \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=api,containerPort=8000"
```

### GCP Deployment

#### Cloud Run

1. **Build and push to GCR:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/research-platform
```

2. **Deploy to Cloud Run:**
```bash
gcloud run deploy research-platform \
  --image gcr.io/PROJECT_ID/research-platform \
  --platform managed \
  --region us-central1 \
  --memory 4Gi \
  --cpu 2 \
  --set-env-vars DATABASE_URL="postgresql://...",REDIS_URL="redis://..." \
  --set-secrets OPENAI_API_KEY=openai-key:latest,ANTHROPIC_API_KEY=anthropic-key:latest \
  --allow-unauthenticated
```

3. **Create Cloud SQL PostgreSQL:**
```bash
gcloud sql instances create research-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-2-8192 \
  --region=us-central1
```

4. **Create Memorystore Redis:**
```bash
gcloud redis instances create research-cache \
  --size=1 \
  --region=us-central1 \
  --redis-version=redis_7_0
```

### Azure Deployment

#### Container Instances

1. **Create resource group:**
```bash
az group create --name research-platform-rg --location eastus
```

2. **Create Azure Database for PostgreSQL:**
```bash
az postgres flexible-server create \
  --resource-group research-platform-rg \
  --name research-db \
  --location eastus \
  --admin-user adminuser \
  --admin-password <password> \
  --sku-name Standard_D2s_v3
```

3. **Create Azure Cache for Redis:**
```bash
az redis create \
  --resource-group research-platform-rg \
  --name research-cache \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

4. **Deploy container:**
```bash
az container create \
  --resource-group research-platform-rg \
  --name research-platform \
  --image your-registry/research-platform:1.0.0 \
  --cpu 2 \
  --memory 4 \
  --ports 8000 \
  --environment-variables \
    DATABASE_URL="postgresql://..." \
    REDIS_URL="redis://..." \
  --secure-environment-variables \
    OPENAI_API_KEY="sk-xxx" \
    ANTHROPIC_API_KEY="sk-ant-xxx"
```

## Environment Variables

### Required
```env
# At least one LLM provider
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=AIzaxxx

# Database
DATABASE_URL=postgresql://user:pass@host:5432/db
```

### Optional
```env
# Additional LLM providers
DEEPSEEK_API_KEY=sk-xxx
QWEN_API_KEY=xxx
XAI_API_KEY=xai-xxx
YI_API_KEY=xxx

# Redis caching
REDIS_URL=redis://host:6379/0

# Paper sources
SEMANTIC_SCHOLAR_API_KEY=xxx

# Configuration
MAX_AGENTS=15
AGENT_TIMEOUT=300
CONSENSUS_THRESHOLD=0.7
MAX_PAPERS_PER_QUERY=50
```

## Scaling Considerations

### Horizontal Scaling
- Run multiple API instances behind load balancer
- Share PostgreSQL and Redis across instances
- Use shared file system (S3/GCS/Azure Blob) for PDFs

### Vertical Scaling
- Minimum: 2 CPU, 4GB RAM
- Recommended: 4 CPU, 8GB RAM
- High load: 8 CPU, 16GB RAM

### Database Scaling
- Use connection pooling (pgBouncer)
- Read replicas for analytics
- Partitioning for large paper collections

### Caching Strategy
- Redis for API responses (2-hour TTL)
- Vector embeddings cached in vector DB
- PDF files on persistent storage

## Monitoring

### Health Checks
```bash
# Liveness probe
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/
```

### Prometheus Metrics
Access at `http://localhost:9090`

Key metrics:
- `papers_processed_total`
- `agent_response_time_seconds`
- `api_request_duration_seconds`
- `consensus_confidence_score`

### Logging
- Structured JSON logs to stdout
- Log level configurable via `LOG_LEVEL`
- Integrate with CloudWatch/Stackdriver/Azure Monitor

## Security

### API Keys
- Store in secrets manager (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)
- Rotate regularly
- Use separate keys for dev/staging/prod

### Network Security
- Run in private subnet
- Use security groups/firewall rules
- Enable VPN/bastion for admin access

### Database
- Use SSL/TLS connections
- Restrict access to API instances only
- Enable encryption at rest

## Backup & Recovery

### Database Backups
```bash
# PostgreSQL backup
pg_dump -h host -U user research_platform > backup.sql

# Restore
psql -h host -U user research_platform < backup.sql
```

### Vector Store Backups
- ChromaDB: Backup `./data/chroma` directory
- Pinecone: Use API snapshots
- Weaviate: Use backup module

### Disaster Recovery
- Automated daily backups
- Multi-region replication for production
- Test recovery procedures monthly

## Performance Tuning

### Database Optimization
```sql
-- Add indexes
CREATE INDEX idx_papers_source ON papers(source);
CREATE INDEX idx_papers_created_at ON papers(created_at);
CREATE INDEX idx_analyses_created_at ON analyses(created_at);
```

### API Optimization
- Enable gzip compression
- Use HTTP/2
- Implement request queuing for rate limiting
- Cache frequent queries

### Agent Optimization
- Reduce `MAX_AGENTS` for faster response
- Use async execution
- Implement circuit breakers for failing APIs

## Troubleshooting

### Common Issues

**Connection errors**
- Check network connectivity
- Verify security groups/firewall rules
- Test database/Redis connections

**Slow responses**
- Check agent timeouts
- Monitor API rate limits
- Review database query performance

**Out of memory**
- Increase container memory
- Reduce concurrent agents
- Enable query result streaming

### Debug Mode
```bash
LOG_LEVEL=DEBUG python main.py
```

### Support
- Check logs: `docker-compose logs -f api`
- Review metrics in Prometheus
- Enable verbose logging for specific modules
