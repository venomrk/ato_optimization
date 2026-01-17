from typing import List, Optional
from datetime import datetime
import httpx
from loguru import logger
from .base import PaperExtractor, Paper, PaperSource


class SemanticScholarExtractor(PaperExtractor):
    BASE_URL = "https://api.semanticscholar.org/graph/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.headers = {}
        if api_key:
            self.headers["x-api-key"] = api_key
    
    def get_source(self) -> PaperSource:
        return PaperSource.SEMANTIC_SCHOLAR
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/paper/search",
                    params={
                        "query": query,
                        "limit": max_results,
                        "fields": "paperId,title,abstract,authors,year,url,openAccessPdf,citationCount,externalIds"
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                papers = []
                for item in data.get("data", []):
                    paper = self._convert_to_paper(item)
                    if paper:
                        papers.append(paper)
                
                logger.info(f"Found {len(papers)} papers from Semantic Scholar for query: {query}")
                return papers
        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []
    
    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/paper/{paper_id}",
                    params={
                        "fields": "paperId,title,abstract,authors,year,url,openAccessPdf,citationCount,externalIds,citations,references"
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return self._convert_to_paper(data)
        except Exception as e:
            logger.error(f"Error fetching Semantic Scholar paper {paper_id}: {e}")
            return None
    
    async def download_pdf(self, paper: Paper, output_path: str) -> bool:
        try:
            if not paper.pdf_url:
                return False
            
            async with httpx.AsyncClient() as client:
                response = await client.get(paper.pdf_url, follow_redirects=True, timeout=60.0)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Downloaded PDF for {paper.paper_id} to {output_path}")
                return True
        except Exception as e:
            logger.error(f"Error downloading PDF for {paper.paper_id}: {e}")
            return False
    
    def _convert_to_paper(self, data: dict) -> Optional[Paper]:
        try:
            paper_id = data.get("paperId")
            if not paper_id:
                return None
            
            title = data.get("title", "")
            abstract = data.get("abstract", "")
            
            authors = []
            for author in data.get("authors", []):
                name = author.get("name", "")
                if name:
                    authors.append(name)
            
            year = data.get("year")
            pub_date = None
            if year:
                try:
                    pub_date = datetime(year, 1, 1)
                except:
                    pass
            
            pdf_url = None
            if data.get("openAccessPdf"):
                pdf_url = data["openAccessPdf"].get("url")
            
            external_ids = data.get("externalIds", {})
            doi = external_ids.get("DOI")
            arxiv_id = external_ids.get("ArXiv")
            
            citations = []
            if data.get("citations"):
                citations = [c.get("paperId") for c in data.get("citations", []) if c.get("paperId")]
            
            return Paper(
                paper_id=f"s2_{paper_id}",
                title=title,
                authors=authors,
                abstract=abstract or "",
                publication_date=pub_date,
                source=self.get_source(),
                source_url=data.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}",
                pdf_url=pdf_url,
                doi=doi,
                citations=citations[:10],
                metadata={
                    "semantic_scholar_id": paper_id,
                    "citation_count": data.get("citationCount"),
                    "arxiv_id": arxiv_id,
                    "external_ids": external_ids,
                }
            )
        except Exception as e:
            logger.error(f"Error converting Semantic Scholar paper: {e}")
            return None
