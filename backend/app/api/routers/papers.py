from __future__ import annotations

import json

try:
    import httpx  # type: ignore
except Exception:  # pragma: no cover
    httpx = None

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import consume_credits, get_current_user
from app.db.models import User
from app.db.session import get_db
from app.schemas.papers import PaperResult, PaperSearchRequest, PaperSearchResponse

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("/search", response_model=PaperSearchResponse)
def search_papers(
    payload: PaperSearchRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if httpx is None:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="httpx dependency not installed")
    if not settings.serpapi_api_key:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Paper search requires SERPAPI_API_KEY (Google Scholar via SerpAPI).",
        )

    consume_credits(db=db, user=user, endpoint="papers.search", credits=1, request_payload=json.dumps(payload.model_dump()))

    params = {
        "engine": "google_scholar",
        "q": payload.query,
        "api_key": settings.serpapi_api_key,
        "num": payload.limit,
    }

    with httpx.Client(timeout=30) as client:
        resp = client.get("https://serpapi.com/search.json", params=params)

    if resp.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Scholar provider error")

    data = resp.json()
    organic = data.get("organic_results") or []

    results: list[PaperResult] = []
    for item in organic[: payload.limit]:
        pub_info = item.get("publication_info") or {}
        summary = pub_info.get("summary")
        authors = None
        year = None
        if isinstance(summary, str):
            authors = summary
        if isinstance(pub_info.get("year"), (str, int)):
            year = str(pub_info.get("year"))

        results.append(
            PaperResult(
                title=item.get("title"),
                link=item.get("link"),
                authors=authors,
                year=year,
                snippet=item.get("snippet"),
            )
        )

    return PaperSearchResponse(query=payload.query, results=results)
