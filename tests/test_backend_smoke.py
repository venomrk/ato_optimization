import os
import sys
import tempfile
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")
pytest.importorskip("jose")
pytest.importorskip("passlib")

_tmpdir = tempfile.TemporaryDirectory()
os.environ.setdefault("DATABASE_URL", f"sqlite+pysqlite:///{Path(_tmpdir.name) / 'test.db'}")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

sys.path.append(str(Path(__file__).resolve().parents[1] / "backend"))

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402


def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_signup_and_me():
    client = TestClient(app)

    r = client.post("/auth/signup", json={"email": "a@example.com", "password": "password123"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    r2 = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r2.status_code == 200
    assert r2.json()["email"] == "a@example.com"
