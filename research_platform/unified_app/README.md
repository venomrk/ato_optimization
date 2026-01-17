# 🚀 Unified Research & Chemistry Platform

The ultimate AI-powered platform combining multi-agent research analysis with interactive chemistry simulation. Built for advanced researchers, chemists, and scientists.

## ✨ Key Features

### 🔬 Research Analysis
- **Multi-Agent System**: 10+ advanced AI models (Claude 3, GPT-4, Gemini, DeepSeek R1)
- **Paper Discovery**: Auto-search from arXiv, PubMed, Semantic Scholar, CrossRef, Google Scholar
- **WHAT/WHY/HOW Analysis**: Structured insights from consensus of AI agents
- **Smart Extraction**: Auto-extract methods, parameters, results from papers

### ⚗️ Chemistry Simulation
- **3D Molecular Visualization**: Real-time WebGL rendering with Three.js
- **Reaction Simulation**: Detailed thermodynamics and molecular dynamics
- **AI Chemistry Chat**: OpenRouter-powered chemistry assistant
- **Parameter Control**: Temperature, pressure, and reaction conditions

### 💎 Subscription & Credits
- **Integrated OpenRouter**: Direct access to 20+ AI models
- **Credit-Based System**: Pay only for what you use
- **Auto-Tracking**: Real-time credit usage and balance updates
- **Flexible Plans**: Free, Basic ($9.99), Pro ($29.99), Enterprise ($99.99)

### 🎨 Advanced UI/UX
- **Dark Theme**: Professional neon aesthetics with glowing effects
- **Real-Time Updates**: WebSocket support for live simulations
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Interactive Dashboard**: Comprehensive stats and activity tracking

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenRouter API key (get one at https://openrouter.ai)
- (Optional) API keys for research sources

### 1. Start the Platform

```bash
cd unified_app
docker-compose up -d
```

### 2. Access the Application

Open your browser to: **http://localhost:3001**

- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Frontend**: http://localhost:3001

### 3. Register an Account

1. Click "Register" on the login screen
2. Fill in your details
3. Select your field of study
4. Get 100 free credits to start!

### 4. Configure OpenRouter

1. Go to Settings → OpenRouter
2. Enter your OpenRouter API key
3. Start using advanced AI models

## 📖 Usage Guide

### Research Analysis Workflow

1. **Navigate to Research Tab**
2. **Enter Research Topic**: e.g., "transparent conducting oxides"
3. **Ask Research Question**: e.g., "What are optimal doping strategies?"
4. **Set Parameters**:
   - Max Papers: 10-50
   - Analysis Types: WHAT, HOW, WHY
5. **Start Analysis**: AI agents will analyze papers
6. **Review Results**: Consensus findings and recommendations

**Example Query**:
```
Topic: quantum computing error correction
Question: What are the most effective error correction codes for NISQ devices?
Max Papers: 20
```

**Cost**: ~200 credits (10 credits per paper × 20 papers)

### Chemistry Simulation Workflow

1. **Navigate to Chemistry Tab**
2. **Adjust Parameters**:
   - Temperature: 200-500 K
   - Pressure: 50000-200000 Pa
3. **Run Simulation**: Get detailed WHAT/WHY/HOW analysis
4. **Ask Chemistry Questions**:
   - "Why does water boil at 100°C?"
   - "What happens in a combustion reaction?"
   - "Explain the Haber process"

**Example Simulation**:
```
Temperature: 373.15 K (100°C)
Pressure: 101325 Pa (1 atm)
Molecule: H₂O
```

**Cost**: 5 credits per simulation

### Using OpenRouter AI

1. **Configure API Key** in settings
2. **Enable in Chat**: Check "Use OpenRouter"
3. **Select Model** based on subscription:
   - Free: GPT-3.5 Turbo
   - Basic: Claude 3 Haiku
   - Pro: Claude 3 Sonnet, GPT-4
   - Enterprise: Claude 3 Opus (all models)

**OpenRouter automatically tracks usage** and deducts from your OpenRouter account.

## 💰 Pricing & Credits

### Subscription Plans

| Plan | Price | Credits/Month | AI Models | Features |
|------|-------|---------------|-----------|----------|
| **Free** | $0 | 100 | GPT-3.5 | 2 agents, basic features |
| **Basic** | $9.99 | 1,000 | Claude 3 Haiku | 5 agents, unlimited research |
| **Pro** | $29.99 | 5,000 | Claude Sonnet, GPT-4 | 10 agents, custom molecules |
| **Enterprise** | $99.99 | 50,000 | All models | 15 agents, white-label |

### Credit Costs

| Action | Credits |
|--------|---------|
| Research paper analysis | 10 per paper |
| Chemistry simulation | 5 per run |
| AI chat (basic) | 1 per message |
| AI chat (OpenRouter) | Variable (tracked separately) |

### Purchase Additional Credits

- **1,000 credits** = $10
- **2,500 credits** = $25 (Best Value!)
- **5,000 credits** = $50

## 🏗️ Architecture

```
Unified Platform
│
├── Frontend (Port 3001)
│   ├── HTML5 + Modern CSS
│   ├── Vanilla JavaScript
│   ├── Three.js (3D visualization)
│   └── Axios (HTTP client)
│
├── Backend (Port 8080)
│   ├── FastAPI
│   ├── Chemistry Engine
│   ├── Multi-Agent System
│   ├── Paper Extractors
│   └── OpenRouter Integration
│
└── External Services
    ├── OpenRouter API
    ├── arXiv, PubMed, etc.
    └── AI Model Providers
```

## 📊 Dashboard Features

### User Stats
- Total research queries
- Chemistry simulations run
- AI messages sent
- Credits used vs. remaining

### Credit Usage
- Real-time balance
- Usage history (last 50 transactions)
- Breakdown by action type
- Usage trends over time

### OpenRouter Status
- Connection status
- Current balance
- Model access level
- Auto-sync with platform

### Recent Activity
- Live activity feed
- Action timestamps
- Credits consumed
- Quick insights

## 🔬 Advanced Research Features

### Multi-Agent Consensus
- Agents analyze independently
- Cross-validate findings
- Identify contradictions
- Weighted voting system
- Confidence scoring

### Paper Processing
- Auto-download PDFs
- Extract metadata
- Parse methodology
- Identify parameters
- Link citations

### Analysis Types

**WHAT Analysis**:
- Key findings
- Main results
- Observations
- Data points

**HOW Analysis**:
- Methodology
- Experimental setup
- Processing steps
- Equipment used

**WHY Analysis**:
- Mechanisms
- Theoretical basis
- Driving forces
- Implications

## ⚗️ Advanced Chemistry Features

### Molecular Simulation
- Brownian motion
- Collision theory
- Transition states
- Energy profiles

### Thermodynamics
- Gibbs free energy (ΔG)
- Enthalpy (ΔH)
- Entropy (ΔS)
- Activation energy

### Reaction Analysis
- Bond breaking/forming
- Electron transfer
- Oxidation states
- Equilibrium constants

### 3D Visualization
- Atomic positions
- Bond types and orders
- Electron clouds
- Molecular orbitals

## 🔐 Security

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt with salt
- **API Key Protection**: Encrypted storage
- **Rate Limiting**: Prevent abuse
- **CORS Protection**: Controlled origins

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Run backend
python unified_api.py

# Serve frontend
cd ../frontend
python -m http.server 3001
```

### Production Deployment

```bash
# Build and deploy
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Variables

Create `.env` file:

```env
# OpenRouter
OPENROUTER_API_KEY=your-key-here

# Optional: Research sources
SEMANTIC_SCHOLAR_API_KEY=xxx
SPRINGER_API_KEY=xxx

# Security
SECRET_KEY=change-to-random-key
```

## 📡 API Reference

### Authentication

```bash
# Register
POST /auth/register
{
  "email": "user@example.com",
  "password": "secure123",
  "username": "researcher",
  "field_of_study": "Chemistry"
}

# Login
POST /auth/login
{
  "email": "user@example.com",
  "password": "secure123"
}

# Get user info
GET /auth/me
Authorization: Bearer <token>
```

### Research

```bash
# Analyze papers
POST /research/analyze
Authorization: Bearer <token>
{
  "query": "quantum computing",
  "research_question": "What are error correction techniques?",
  "max_papers": 10,
  "analysis_types": ["what", "how", "why"]
}
```

### Chemistry

```bash
# Run simulation
POST /chemistry/simulate
Authorization: Bearer <token>
{
  "message": "water molecule",
  "temperature": 373.15,
  "pressure": 101325
}

# Chemistry chat
POST /chemistry/chat?message=Why does water boil?&use_openrouter=true
Authorization: Bearer <token>
```

### Credits

```bash
# Get usage
GET /credits/usage
Authorization: Bearer <token>

# Purchase credits
POST /credits/purchase
Authorization: Bearer <token>
Content-Type: application/json
50  # Amount in dollars
```

### OpenRouter

```bash
# Configure API key
POST /openrouter/configure
Authorization: Bearer <token>
Content-Type: text/plain
sk-or-v1-xxxxx  # Your OpenRouter API key

# Check balance
GET /openrouter/balance
Authorization: Bearer <token>
```

## 🎯 Use Cases

### Academic Research
- Literature review
- Trend analysis
- Methodology comparison
- Gap identification

### Chemistry Education
- Visualize reactions
- Understand mechanisms
- Learn thermodynamics
- Practice problem-solving

### Drug Discovery
- Analyze synthesis routes
- Study molecular interactions
- Optimize parameters
- Review clinical trials

### Materials Science
- Research novel materials
- Optimize processing
- Understand properties
- Compare methodologies

## 🔮 Roadmap

### Phase 1 (Current)
- ✅ Multi-agent research
- ✅ Chemistry simulation
- ✅ OpenRouter integration
- ✅ Credit system
- ✅ Advanced UI

### Phase 2 (Q2 2025)
- [ ] Mobile app (React Native)
- [ ] Collaborative features
- [ ] Custom AI fine-tuning
- [ ] Export to lab notebooks
- [ ] API marketplace

### Phase 3 (Q3 2025)
- [ ] VR chemistry lab
- [ ] Quantum chemistry
- [ ] ML property prediction
- [ ] Lab equipment integration
- [ ] Enterprise SSO

## 🤝 Support

- **Documentation**: This README + inline help
- **API Docs**: http://localhost:8080/docs
- **Issues**: GitHub Issues
- **Email**: support@research-chem-platform.ai

## 📝 License

MIT License - Open source and free to use

---

## 🎉 Getting Started Checklist

- [ ] Install Docker
- [ ] Get OpenRouter API key
- [ ] Run `docker-compose up -d`
- [ ] Open http://localhost:3001
- [ ] Register account
- [ ] Configure OpenRouter key
- [ ] Run first research analysis
- [ ] Try chemistry simulation
- [ ] Explore dashboard

**Version**: 2.0.0  
**Status**: Production Ready ✅  
**Last Updated**: 2025-01-17

---

**🚀 Start analyzing research and simulating chemistry today!** 🧪
