from typing import List, Optional
from datetime import datetime
import httpx
from loguru import logger
from .base import PaperExtractor, Paper, PaperSource


class CrossRefExtractor(PaperExtractor):
    BASE_URL = "https://api.crossref.org"
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.headers = {"User-Agent": "ResearchPlatform/1.0 (mailto:research@platform.ai)"}
    
    def get_source(self) -> PaperSource:
        return PaperSource.CROSSREF
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/works",
                    params={
                        "query": query,
                        "rows": max_results,
                        "select": "DOI,title,author,abstract,published-print,URL,link,type"
                    },
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                papers = []
                for item in data.get("message", {}).get("items", []):
                    paper = self._convert_to_paper(item)
                    if paper:
                        papers.append(paper)
                
                logger.info(f"Found {len(papers)} papers from CrossRef for query: {query}")
                return papers
        except Exception as e:
            logger.error(f"Error searching CrossRef: {e}")
            return []
    
    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        try:
            doi = paper_id.replace("crossref_", "")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/works/{doi}",
                    headers=self.headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return self._convert_to_paper(data.get("message", {}))
        except Exception as e:
            logger.error(f"Error fetching CrossRef paper {paper_id}: {e}")
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
            doi = data.get("DOI")
            if not doi:
                return None
            
            title_list = data.get("title", [])
            title = title_list[0] if title_list else ""
            
            abstract = data.get("abstract", "")
            
            authors = []
            for author in data.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                name = f"{given} {family}".strip()
                if name:
                    authors.append(name)
            
            pub_date = None
            date_parts = data.get("published-print", {}).get("date-parts")
            if not date_parts:
                date_parts = data.get("published-online", {}).get("date-parts")
            if date_parts and len(date_parts) > 0 and len(date_parts[0]) > 0:
                try:
                    year = date_parts[0][0]
                    month = date_parts[0][1] if len(date_parts[0]) > 1 else 1
                    day = date_parts[0][2] if len(date_parts[0]) > 2 else 1
                    pub_date = datetime(year, month, day)
                except:
                    pass
            
            pdf_url = None
            for link in data.get("link", []):
                if link.get("content-type") == "application/pdf":
                    pdf_url = link.get("URL")
                    break
            
            url = data.get("URL", f"https://doi.org/{doi}")
            
            return Paper(
                paper_id=f"crossref_{doi.replace('/', '_')}",
                title=title,
                authors=authors,
                abstract=abstract or "",
                publication_date=pub_date,
                source=self.get_source(),
                source_url=url,
                pdf_url=pdf_url,
                doi=doi,
                metadata={
                    "type": data.get("type"),
                    "publisher": data.get("publisher"),
                    "journal": data.get("container-title", [None])[0],
                    "volume": data.get("volume"),
                    "issue": data.get("issue"),
                    "page": data.get("page"),
                }
            )
        except Exception as e:
            logger.error(f"Error converting CrossRef paper: {e}")
            return None
