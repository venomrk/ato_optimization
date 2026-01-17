from __future__ import annotations

from pydantic import BaseModel, Field


class PaperSearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=300)
    limit: int = Field(default=10, ge=1, le=20)


class PaperResult(BaseModel):
    title: str | None = None
    link: str | None = None
    authors: str | None = None
    year: str | None = None
    snippet: str | None = None


class PaperSearchResponse(BaseModel):
    query: str
    results: list[PaperResult]
