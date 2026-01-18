from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.init_db import init_db
from app.api.routers import auth, billing, chat, health, papers, users

app = FastAPI(title="RKO Research Chemistry Platform", version="0.1.0")

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(papers.router)
app.include_router(chat.router)
app.include_router(billing.router)
