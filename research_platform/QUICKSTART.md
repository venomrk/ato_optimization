# Quick Start Guide

Get the Multi-Agent Research Analysis Platform running in under 5 minutes!

## Prerequisites

- Docker & Docker Compose (recommended)
  OR
- Python 3.11+ (for local development)
- API keys for at least one LLM provider

## Option 1: Docker (Recommended)

### Step 1: Configure API Keys

```bash
cd research_platform
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Required: Add at least ONE of these
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=AIzaxxx

# Optional: Add for more agents
DEEPSEEK_API_KEY=sk-xxx
QWEN_API_KEY=xxx
XAI_API_KEY=xai-xxx
```

### Step 2: Start the Platform

```bash
docker-compose up -d
```

Wait ~10 seconds for services to initialize.

### Step 3: Verify

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "agents_available": 10,
  "database": "connected",
  "vector_store": "connected"
}
```

### Step 4: Your First Analysis

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning transformers",
    "research_question": "What are the key innovations in transformer architectures?",
    "max_papers": 5,
    "run_full_analysis": false
  }'
```

**That's it!** The platform is now analyzing research papers with multiple AI agents.

## Option 2: Local Python

### Step 1: Install Dependencies

```bash
cd research_platform
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### Step 2: Configure

```bash
cp .env.example .env
# Edit .env with your API keys
```

### Step 3: Run

```bash
python main.py
```

API available at: `http://localhost:8000`

## Using the CLI

### Check Available Agents

```bash
python cli.py agents
```

### Search Papers

```bash
python cli.py search "quantum computing" --max-results=10
```

### Analyze Research

```bash
python cli.py analyze \
  "neural networks" \
  "What activation functions perform best?" \
  --max-papers=10
```

## Quick Examples

### Example 1: Material Science

```python
import httpx
import asyncio

async def analyze_materials():
    async with httpx.AsyncClient(timeout=600.0) as client:
        response = await client.post(
            "http://localhost:8000/analyze",
            json={
                "query": "transparent conducting oxides",
                "research_question": "What doping strategies improve conductivity?",
                "max_papers": 10
            }
        )
        results = response.json()
        print(f"Confidence: {results['analysis_results']['general']['consensus']['confidence_score']:.1%}")
        for finding in results['analysis_results']['general']['consensus']['key_findings'][:3]:
            print(f"- {finding}")

asyncio.run(analyze_materials())
```

### Example 2: Using Make

```bash
# Start platform
make docker-up

# Check agents
make check-agents

# Run example
make example

# Search papers
make cli-search QUERY="solar cells"

# Stop platform
make docker-down
```

## API Documentation

Interactive documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Understanding the Results

When you run an analysis, you get:

### 1. Agent Responses
Each agent's individual analysis with:
- Response text
- Reasoning chain (thought process)
- Confidence score
- Key claims
- Evidence

### 2. Consensus Results
Synthesized findings with:
- Consolidated answer
- Overall confidence (0-1)
- Agreement level between agents
- Key findings (weighted by agent votes)
- Contradictions detected
- Recommendations

### 3. Analysis Types
- **WHAT**: Key findings, materials, results
- **HOW**: Methodology, procedures, techniques  
- **WHY**: Mechanisms, rationale, significance

## Troubleshooting

### No agents available
```bash
# Check your API keys
python cli.py agents

# Verify .env file exists and has valid keys
cat .env | grep API_KEY
```

### Connection refused
```bash
# Check if services are running
docker-compose ps

# View logs
docker-compose logs api
```

### Slow responses
```bash
# Reduce number of agents in .env
MAX_AGENTS=5

# Reduce papers analyzed
# In API request: "max_papers": 5
```

### Docker issues
```bash
# Restart services
docker-compose restart

# Full reset
docker-compose down
docker-compose up -d
```

## Next Steps

1. **Read the Full Documentation**: `README.md`
2. **Explore Examples**: `EXAMPLES.md`
3. **Deploy to Production**: `DEPLOYMENT.md`
4. **Check Project Details**: `PROJECT_OVERVIEW.md`

## Common Tasks

### Add More API Keys

Edit `.env`:
```env
# Multiple OpenAI keys
OPENAI_API_KEY=sk-xxx
OPENAI_API_KEY_2=sk-yyy
OPENAI_API_KEY_3=sk-zzz

# Multiple Anthropic keys
ANTHROPIC_API_KEY=sk-ant-xxx
ANTHROPIC_API_KEY_2=sk-ant-yyy
```

Restart: `docker-compose restart`

### View Logs

```bash
# All services
docker-compose logs -f

# Just API
docker-compose logs -f api

# Last 100 lines
docker-compose logs --tail=100 api
```

### Access Database

```bash
docker-compose exec postgres psql -U research -d research_platform

# List papers
SELECT paper_id, title FROM papers LIMIT 10;

# Recent analyses
SELECT query, confidence_score FROM analyses ORDER BY created_at DESC LIMIT 5;
```

### Clear Cache

```bash
docker-compose exec redis redis-cli FLUSHDB
```

## Configuration Quick Reference

### Essential Settings

```env
# Agent behavior
MAX_AGENTS=15              # Number of agents (1-15)
AGENT_TIMEOUT=300          # Timeout per agent (seconds)
CONSENSUS_THRESHOLD=0.7    # Agreement threshold (0-1)

# Paper search
MAX_PAPERS_PER_QUERY=50    # Max papers to fetch

# Performance
API_WORKERS=4              # Concurrent API workers
```

### Storage Paths

```env
PAPER_STORAGE_PATH=./data/papers    # PDF storage
MODEL_STORAGE_PATH=./data/models    # Fine-tuned models
CACHE_DIR=./data/cache              # Temporary cache
```

## Resources

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health  
- **Agent Status**: http://localhost:8000/agents
- **Recent Analyses**: http://localhost:8000/analyses

## Support

### Check System Status

```bash
# All services healthy?
docker-compose ps

# API responding?
curl http://localhost:8000/health

# Agents available?
curl http://localhost:8000/agents
```

### Common Questions

**Q: How many agents do I need?**
A: Minimum 3-5 for good consensus. Optimal: 10-15.

**Q: Which API keys are required?**
A: At least one provider (OpenAI, Anthropic, or Google). More providers = better consensus.

**Q: How long does analysis take?**
A: 30-60 seconds for 10 papers with 10 agents (agents run in parallel).

**Q: Can I use without Docker?**
A: Yes! Just run `python main.py` after installing dependencies.

**Q: How much does it cost?**
A: Depends on your API usage. Typical analysis with 10 papers: $0.50-$2.00 per query.

## Getting Help

1. Check logs: `docker-compose logs -f api`
2. Verify health: `curl http://localhost:8000/health`
3. Test agents: `python cli.py agents`
4. Review documentation: `README.md`

---

**You're ready to go!** Start analyzing research papers with AI agents. 🚀
