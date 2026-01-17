# RKO Multi‑Agent Research Chemistry Platform (MVP)

This repository contains a minimal, production-oriented MVP for a **multi-agent research + chemistry chat platform**.

It includes:
- **FastAPI backend** (JWT auth, users, credits, paper search, OpenRouter chat, Stripe billing endpoints)
- **React frontend** (login/signup, dashboard, research search, chat, profile/billing)
- **Docker + docker-compose** for local/prod-like deployment

> Note: This repo originally contained AFTO smart-glass simulation scripts (`physics_engine.py`, `ml_optimizer.py`, `generate_recipe.py`). They are still present and can be used independently.

## Architecture (MVP)
- Frontend: React (Vite) served by Nginx
- Backend: FastAPI (Uvicorn)
- DB: PostgreSQL (or SQLite for dev)
- Optional: Redis (not required for MVP runtime; reserved for rate limiting/background jobs)

## Local run (Docker)

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

## Backend endpoints (high level)
- `POST /auth/signup` – create user (Free tier: 100 credits)
- `POST /auth/login` – JWT login
- `GET /users/me` – current user
- `POST /papers/search` – Google Scholar via SerpAPI
- `POST /chat/completions` – multi-agent chat via OpenRouter
- `POST /billing/checkout-session` – Stripe checkout session
- `POST /billing/webhook` – Stripe webhook receiver

## Production deployment (AWS ECS Fargate – minimal)
See `infra/aws/README.md` for a minimal ECS/Fargate + ALB outline and example task definitions.

## Configuration
See `.env.example` for all environment variables.

## License
MIT – see `LICENSE`.
