# Multi-Agent Research Analysis Platform - Documentation Index

## 🚀 Quick Navigation

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Get running in under 5 minutes
- **[README.md](README.md)** - Complete platform documentation
- **[EXAMPLES.md](EXAMPLES.md)** - Usage examples and code samples

### Deployment
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide (AWS/GCP/Azure)
- **[docker-compose.yml](docker-compose.yml)** - Local development stack
- **[Dockerfile](Dockerfile)** - Container configuration

### Understanding the System
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Architecture and design
- **[SUCCESS_CRITERIA.md](SUCCESS_CRITERIA.md)** - Requirements validation

### Configuration
- **[.env.example](.env.example)** - Environment variables template
- **[Makefile](Makefile)** - Common commands
- **[requirements.txt](requirements.txt)** - Python dependencies

## 📚 Documentation by Topic

### For First-Time Users
1. Read: **[QUICKSTART.md](QUICKSTART.md)**
2. Run: `docker-compose up -d`
3. Test: `curl http://localhost:8000/health`
4. Explore: `http://localhost:8000/docs` (interactive API docs)

### For Developers
1. Architecture: **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**
2. Code Examples: **[EXAMPLES.md](EXAMPLES.md)**
3. API Reference: `http://localhost:8000/docs`
4. Tests: `pytest tests/ -v`

### For DevOps/Deployment
1. Local: **[QUICKSTART.md](QUICKSTART.md)** - Docker Compose
2. Cloud: **[DEPLOYMENT.md](DEPLOYMENT.md)** - AWS/GCP/Azure guides
3. Monitoring: **[prometheus.yml](prometheus.yml)**
4. Configuration: **[.env.example](.env.example)**

### For Researchers
1. Usage: **[README.md](README.md)** - Core concepts
2. Examples: **[EXAMPLES.md](EXAMPLES.md)** - Research workflows
3. CLI: `python cli.py --help`
4. Scripts: `scripts/example_query.py`

## 🗂️ Source Code Structure

### Paper Extraction (`extractors/`)
- `base.py` - Base classes and Paper model
- `arxiv_extractor.py` - arXiv API integration
- `pubmed_extractor.py` - PubMed API integration
- `semantic_scholar_extractor.py` - Semantic Scholar API
- `crossref_extractor.py` - CrossRef API
- `google_scholar_extractor.py` - Google Scholar
- `pdf_processor.py` - PDF text and data extraction
- `orchestrator.py` - Multi-source coordination

### Multi-Agent System (`agents/`)
- `base.py` - Agent interface and response models
- `claude_agent.py` - Claude 3 (Anthropic)
- `openai_agent.py` - GPT-4, o1, o3 (OpenAI)
- `gemini_agent.py` - Gemini 2.0 (Google)
- `generic_agent.py` - DeepSeek, Qwen, Grok, Yi
- `agent_factory.py` - Agent creation and pooling
- `orchestrator.py` - Multi-agent coordination
- `consensus.py` - Consensus building engine

### Storage Layer (`storage/`)
- `database.py` - PostgreSQL ORM (papers, analyses, models)
- `vector_store.py` - ChromaDB for embeddings
- `cache.py` - Redis caching

### API (`api/`)
- `app.py` - FastAPI application with endpoints

### Configuration (`config/`)
- `settings.py` - Pydantic settings management

### Scripts (`scripts/`)
- `example_query.py` - Example multi-agent analysis
- `check_agents.py` - Agent availability check
- `verify_installation.py` - Installation verification

### Tests (`tests/`)
- `test_extractors.py` - Paper extraction tests
- `test_consensus.py` - Consensus engine tests

## 🎯 Common Tasks

### Installation & Setup
```bash
# Quick start
cp .env.example .env
# Edit .env with API keys
docker-compose up -d

# Or use Makefile
make quickstart
make docker-up
```

### Verify Installation
```bash
python scripts/verify_installation.py
python scripts/check_agents.py
```

### Search Papers
```bash
# Via CLI
python cli.py search "quantum computing" --max-results=10

# Via API
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "quantum computing", "max_results": 10}'
```

### Analyze Research
```bash
# Via CLI
python cli.py analyze \
  "machine learning" \
  "What are the latest techniques?" \
  --max-papers=10

# Via API
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "query": "machine learning",
    "research_question": "What are the latest techniques?",
    "max_papers": 10
  }'
```

### Run Examples
```bash
make example
# Or directly
python scripts/example_query.py
```

### Development
```bash
# Install dev dependencies
make setup-dev

# Run tests
make test

# Format code
make format

# Lint code
make lint
```

## 🔍 Finding Information

### "How do I...?"

#### Set up the platform?
→ **[QUICKSTART.md](QUICKSTART.md)**

#### Deploy to production?
→ **[DEPLOYMENT.md](DEPLOYMENT.md)**

#### Add a new paper source?
→ **[README.md](README.md)** - "Extending the Platform" section

#### Add a new AI agent?
→ `agents/agent_factory.py` - Add to `create_agent_pool()`

#### Understand the architecture?
→ **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**

#### See example code?
→ **[EXAMPLES.md](EXAMPLES.md)**

#### Configure settings?
→ **[.env.example](.env.example)** - All environment variables

#### Troubleshoot issues?
→ **[QUICKSTART.md](QUICKSTART.md)** - Troubleshooting section

### "What is...?"

#### The consensus mechanism?
→ `agents/consensus.py` + **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)**

#### WHAT/HOW/WHY analysis?
→ **[README.md](README.md)** - "Analysis Types" section

#### Agent weighting?
→ `agents/consensus.py` - `_calculate_agent_weights()` method

#### Paper deduplication?
→ `extractors/orchestrator.py` - `_deduplicate_papers()` method

### "Where is...?"

#### API documentation?
→ `http://localhost:8000/docs` (Swagger UI)

#### Configuration settings?
→ `config/settings.py` + **[.env.example](.env.example)**

#### Database schema?
→ `storage/database.py` - SQLAlchemy models

#### Example queries?
→ **[EXAMPLES.md](EXAMPLES.md)** + `scripts/example_query.py`

## 📊 Feature Matrix

| Feature | File/Module | Documentation |
|---------|-------------|---------------|
| Paper Search | `extractors/orchestrator.py` | [README.md](README.md) |
| PDF Processing | `extractors/pdf_processor.py` | [README.md](README.md) |
| Multi-Agent Analysis | `agents/orchestrator.py` | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |
| Consensus Building | `agents/consensus.py` | [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) |
| API Endpoints | `api/app.py` | `http://localhost:8000/docs` |
| Database | `storage/database.py` | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Vector Search | `storage/vector_store.py` | [README.md](README.md) |
| Caching | `storage/cache.py` | [DEPLOYMENT.md](DEPLOYMENT.md) |
| CLI Tool | `cli.py` | [EXAMPLES.md](EXAMPLES.md) |

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v --cov=.
```

### Run Specific Tests
```bash
pytest tests/test_extractors.py -v
pytest tests/test_consensus.py -v
```

### Integration Testing
```bash
python scripts/verify_installation.py
python scripts/example_query.py
```

## 📖 API Reference

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Core Endpoints
- `GET /` - Service info
- `GET /health` - Health check
- `POST /search` - Search papers
- `POST /analyze` - Multi-agent analysis
- `GET /analyses` - Recent analyses
- `GET /agents` - List agents
- `POST /papers/{id}/enrich` - Enrich paper

## 🔧 Configuration Reference

### Essential Settings
```env
OPENAI_API_KEY=sk-xxx          # OpenAI (GPT-4, o1, o3)
ANTHROPIC_API_KEY=sk-ant-xxx   # Claude 3
GOOGLE_API_KEY=AIzaxxx         # Gemini 2.0
DATABASE_URL=postgresql://...  # Database connection
```

### Optional Settings
```env
DEEPSEEK_API_KEY=sk-xxx        # DeepSeek R1
QWEN_API_KEY=xxx               # Qwen QwQ
XAI_API_KEY=xai-xxx            # Grok-2
YI_API_KEY=xxx                 # Yi-Lightning
REDIS_URL=redis://...          # Caching
MAX_AGENTS=15                  # Agent pool size
AGENT_TIMEOUT=300              # Agent timeout (seconds)
```

Full list: **[.env.example](.env.example)**

## 📦 Project Statistics

- **Total Files**: 40+
- **Lines of Code**: 5000+
- **Paper Sources**: 5
- **AI Models Supported**: 12+
- **API Endpoints**: 7
- **Documentation Files**: 8
- **Test Files**: 2
- **Example Scripts**: 3

## 🤝 Contributing

### Code Structure
- Follow existing patterns in each module
- Add tests for new features
- Update documentation
- Use Pydantic for data validation
- Add type hints

### Testing New Features
1. Add unit tests to `tests/`
2. Run: `pytest tests/ -v`
3. Verify with example script
4. Update documentation

## 🆘 Getting Help

### Quick Checks
1. Health: `curl http://localhost:8000/health`
2. Agents: `python cli.py agents`
3. Logs: `docker-compose logs -f api`
4. Verify: `python scripts/verify_installation.py`

### Common Issues
- **No agents**: Check API keys in `.env`
- **Connection errors**: Verify Docker containers running
- **Slow analysis**: Reduce `MAX_AGENTS` or `max_papers`
- **PDF errors**: Some papers behind paywalls

See **[QUICKSTART.md](QUICKSTART.md)** - Troubleshooting section

## 📋 Checklist for New Users

- [ ] Read [QUICKSTART.md](QUICKSTART.md)
- [ ] Copy `.env.example` to `.env`
- [ ] Add at least one API key
- [ ] Run `docker-compose up -d`
- [ ] Check health: `curl http://localhost:8000/health`
- [ ] View agents: `python cli.py agents`
- [ ] Try example: `make example`
- [ ] Read [API docs](http://localhost:8000/docs)
- [ ] Try your own query!

## 🎓 Learning Path

### Beginner
1. **[QUICKSTART.md](QUICKSTART.md)** - Setup and first run
2. **[EXAMPLES.md](EXAMPLES.md)** - Basic examples
3. CLI: `python cli.py --help`

### Intermediate
1. **[README.md](README.md)** - Core concepts
2. **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** - Architecture
3. Explore API: `http://localhost:8000/docs`
4. Run tests: `pytest tests/ -v`

### Advanced
1. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment
2. Source code: `agents/`, `extractors/`, `storage/`
3. Extend: Add new sources, agents, or features
4. Contribute: Submit improvements

## 📞 Support Resources

- **Documentation**: This INDEX + linked files
- **API Docs**: http://localhost:8000/docs
- **Example Code**: `scripts/` directory
- **Test Suite**: `tests/` directory
- **Configuration**: `.env.example`

## ✅ Verification

Platform working correctly if:
- [ ] `python scripts/verify_installation.py` passes
- [ ] `curl http://localhost:8000/health` returns healthy
- [ ] `python cli.py agents` shows 3+ agents
- [ ] `python scripts/example_query.py` completes successfully
- [ ] API docs load at `http://localhost:8000/docs`

## 🎉 You're Ready!

**Start analyzing research papers with AI agents:**

```bash
python cli.py analyze \
  "your research topic" \
  "your specific question" \
  --max-papers=10
```

Happy researching! 🚀
