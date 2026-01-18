from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class PaperSource(str, Enum):
    ARXIV = "arxiv"
    PUBMED = "pubmed"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    GOOGLE_SCHOLAR = "google_scholar"
    CROSSREF = "crossref"
    MANUAL = "manual"


class ProcessingParameter(BaseModel):
    name: str
    value: str
    unit: Optional[str] = None
    category: Optional[str] = None


class ExperimentalMethod(BaseModel):
    description: str
    equipment: List[str] = Field(default_factory=list)
    materials: List[str] = Field(default_factory=list)
    parameters: List[ProcessingParameter] = Field(default_factory=list)


class Result(BaseModel):
    measurement: str
    value: Optional[str] = None
    unit: Optional[str] = None
    description: str


class Paper(BaseModel):
    paper_id: str
    title: str
    authors: List[str]
    abstract: str
    publication_date: Optional[datetime] = None
    source: PaperSource
    source_url: Optional[str] = None
    pdf_url: Optional[str] = None
    pdf_path: Optional[str] = None
    doi: Optional[str] = None
    
    key_findings: List[str] = Field(default_factory=list)
    experimental_methods: List[ExperimentalMethod] = Field(default_factory=list)
    results: List[Result] = Field(default_factory=list)
    materials: List[str] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=list)
    processing_parameters: List[ProcessingParameter] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    
    full_text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class PaperExtractor(ABC):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        pass
    
    @abstractmethod
    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        pass
    
    @abstractmethod
    async def download_pdf(self, paper: Paper, output_path: str) -> bool:
        pass
    
    def get_source(self) -> PaperSource:
        return PaperSource.MANUAL
