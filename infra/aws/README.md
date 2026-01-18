# AWS deployment (minimal ECS Fargate outline)

This folder provides a **minimal starting point** for deploying the Dockerized MVP to AWS.

## Recommended minimal production setup
- Route53 / rko.ai DNS
- ACM certificate (for `rko.ai` and `api.rko.ai`)
- ALB (HTTPS)
- ECS Fargate cluster
  - Service `rko-backend` (FastAPI)
  - Service `rko-frontend` (Nginx static React)
- RDS Postgres
- (Optional) ElastiCache Redis

## Files
- `task-def-backend.json` – example ECS task definition for FastAPI
- `task-def-frontend.json` – example ECS task definition for React/Nginx

## Notes
1. Build & push images to ECR:
   - `backend`: `./backend/Dockerfile`
   - `frontend`: `./frontend/Dockerfile`
2. Configure backend env vars in the task definition (Secrets Manager recommended):
   - `DATABASE_URL`
   - `JWT_SECRET_KEY`
   - `OPENROUTER_API_KEY`
   - `SERPAPI_API_KEY`
   - `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PREMIUM_PRICE_ID`
3. Set `CORS_ORIGINS` to your production frontend origin (e.g. `https://rko.ai`).
4. For the frontend build, set `VITE_API_BASE_URL=https://api.rko.ai`.

These files are intentionally minimal to keep the MVP shippable; production hardening should add:
- WAF
- structured logging
- rate limiting
- database migrations (Alembic)
- background jobs (Celery/RQ)
