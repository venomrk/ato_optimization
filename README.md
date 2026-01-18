# 🚀 RKO Multi‑Agent Research Chemistry Platform

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/multi-agent-research-advanced-materials)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/yourusername/multi-agent-research-advanced-materials)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/yourusername/multi-agent-research-advanced-materials)

**A production-ready multi-agent research and chemistry chat platform with 100% FREE deployment options!**

## ✨ Features

- 🤖 **Multi-Agent Research System** - AI-powered research assistants
- 🧪 **Chemistry Interface** - Interactive chemistry tools and simulations
- 🔐 **JWT Authentication** - Secure user authentication
- 💳 **Stripe Integration** - Payment processing and subscriptions
- 📚 **Academic Search** - Google Scholar, arXiv, PubMed integration
- 💬 **AI Chat** - OpenRouter integration for advanced conversations
- 🎯 **Credit System** - Token-based usage tracking
- 🔄 **Real-time Updates** - Live research results
- 📱 **Responsive Design** - Works on all devices

## 🎯 Quick Deploy (FREE)

**Deploy in under 5 minutes with ZERO cost!**

### Option 1: Vercel + Railway (Recommended)

**Frontend (Vercel):**
1. Fork this repository
2. Go to [vercel.com](https://vercel.com) and import your repo
3. Set `Root Directory` to `frontend`
4. Add environment variable: `VITE_API_BASE_URL=https://your-backend.railway.app`
5. Deploy! ✅ Live at `https://your-project.vercel.app`

**Backend (Railway):**
1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select this repository
4. Add PostgreSQL database (one-click)
5. Set environment variables (see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md))
6. Deploy! ✅ Live at `https://your-project.railway.app`

**Full deployment guide:** [📖 DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Option 2: Render (All-in-One)

1. Go to [render.com](https://render.com)
2. Click "New Blueprint"
3. Connect this repository
4. Render deploys everything automatically using `render.yaml`
5. Done! ✅ Live at `https://your-project.onrender.com`

### Option 3: Quick Deploy Script

```bash
bash deploy.sh
```

Follow the interactive prompts to deploy to your chosen platform.

## 🏗️ Architecture

This repository contains:
- **FastAPI backend** (JWT auth, users, credits, paper search, OpenRouter chat, Stripe billing)
- **React frontend** (login/signup, dashboard, research search, chat, profile/billing)
- **Docker + docker-compose** for local development
- **Original AFTO scripts** (`physics_engine.py`, `ml_optimizer.py`, `generate_recipe.py`)

### Tech Stack

**Frontend:**
- React 18 + Vite
- React Router
- Modern CSS

**Backend:**
- FastAPI
- SQLAlchemy + PostgreSQL
- JWT Authentication
- Stripe API
- OpenRouter API
- SerpAPI (Google Scholar)

## 💻 Local Development

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start with Docker

1) Copy env example:
```bash
cp .env.example .env
```

2) Start:
```bash
docker compose up --build
```

3) Open:
- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs

### Manual Setup (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your backend URL
npm run dev
```

## 📡 API Endpoints

### Authentication
- `POST /auth/signup` – Create user (Free tier: 100 credits)
- `POST /auth/login` – JWT login
- `GET /auth/me` – Get current user

### Users
- `GET /users/me` – Current user profile
- `PATCH /users/me` – Update profile

### Research
- `POST /papers/search` – Search academic papers (Google Scholar)
- `GET /papers/{id}` – Get paper details

### AI Chat
- `POST /chat/completions` – Multi-agent chat via OpenRouter
- `GET /chat/history` – Get chat history

### Billing
- `POST /billing/checkout-session` – Create Stripe checkout
- `POST /billing/webhook` – Stripe webhook handler
- `GET /billing/subscriptions` – User subscriptions

### Health
- `GET /health` – Health check endpoint

**Full API documentation:** Visit `http://localhost:8000/docs` (Swagger UI)

## 🔧 Configuration

### Backend Environment Variables

See [`.env.production.example`](.env.production.example) for all variables.

**Required:**
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-min-32-chars
CORS_ORIGINS=https://your-frontend.vercel.app
```

**Optional (for full features):**
```bash
OPENROUTER_API_KEY=sk-or-v1-...
SERP_API_KEY=your-serp-key
STRIPE_SECRET_KEY=sk_test_...
REDIS_URL=redis://...
```

### Frontend Environment Variables

See [`frontend/.env.example`](frontend/.env.example)

```bash
VITE_API_BASE_URL=https://your-backend.railway.app
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## 🌐 Free Hosting Options

| Platform | Best For | Database | Cost |
|----------|----------|----------|------|
| **Vercel** | Frontend | - | FREE |
| **Railway** | Backend + DB | PostgreSQL ✅ | FREE ($5 credit/month) |
| **Render** | Full Stack | PostgreSQL ✅ | FREE |
| **Netlify** | Frontend | - | FREE |

**Detailed guide:** [📖 DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🧪 Testing

### Test User Registration
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User"}'
```

### Test Stripe (Test Mode)
Use test card: `4242 4242 4242 4242`
- Expiry: Any future date
- CVC: Any 3 digits
- ZIP: Any 5 digits

## 📦 Project Structure

```
.
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/          # API routes
│   │   ├── core/         # Config, security
│   │   ├── db/           # Database models
│   │   └── schemas/      # Pydantic schemas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/             # React frontend
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── pages/        # Page components
│   │   └── App.jsx       # Main app
│   ├── package.json
│   └── vite.config.js
├── research_platform/    # Research CLI tools
├── infra/                # Infrastructure configs
├── vercel.json           # Vercel config
├── railway.toml          # Railway config
├── render.yaml           # Render config
├── netlify.toml          # Netlify config
├── docker-compose.yml    # Local development
├── deploy.sh             # Quick deploy script
└── DEPLOYMENT_GUIDE.md   # Detailed deployment guide
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenRouter** for AI chat capabilities
- **Stripe** for payment processing
- **Google Scholar** via SerpAPI for academic search
- **FastAPI** and **React** communities

## 📞 Support

- 📖 **Documentation:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- 🐛 **Issues:** [GitHub Issues](https://github.com/yourusername/multi-agent-research-advanced-materials/issues)
- 💬 **Discussions:** [GitHub Discussions](https://github.com/yourusername/multi-agent-research-advanced-materials/discussions)

## 🚀 What's Next?

After deploying:
1. ✅ Set up monitoring (Sentry, LogRocket)
2. ✅ Configure custom domain
3. ✅ Enable auto-scaling
4. ✅ Add more AI agents
5. ✅ Enhance chemistry simulations
6. ✅ Implement real-time collaboration

---

**Built with ❤️ for the research community**

**Deploy now for FREE!** 🚀
