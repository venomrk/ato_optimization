from typing import List, Optional
from datetime import datetime
import httpx
from scholarly import scholarly
from loguru import logger
import asyncio
from .base import PaperExtractor, Paper, PaperSource


class GoogleScholarExtractor(PaperExtractor):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
    
    def get_source(self) -> PaperSource:
        return PaperSource.GOOGLE_SCHOLAR
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        try:
            loop = asyncio.get_event_loop()
            search_query = await loop.run_in_executor(
                None, 
                lambda: list(scholarly.search_pubs(query))[:max_results]
            )
            
            papers = []
            for result in search_query:
                paper = await self._convert_to_paper(result)
                if paper:
                    papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers from Google Scholar for query: {query}")
            return papers
        except Exception as e:
            logger.error(f"Error searching Google Scholar: {e}")
            return []
    
    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        try:
            return None
        except Exception as e:
            logger.error(f"Error fetching Google Scholar paper {paper_id}: {e}")
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
    
    async def _convert_to_paper(self, result: dict) -> Optional[Paper]:
        try:
            bib = result.get("bib", {})
            
            title = bib.get("title", "")
            if not title:
                return None
            
            abstract = bib.get("abstract", "")
            
            authors = []
            author_str = bib.get("author", "")
            if author_str:
                if isinstance(author_str, list):
                    authors = author_str
                else:
                    authors = [a.strip() for a in author_str.split(" and ")]
            
            year = bib.get("pub_year")
            pub_date = None
            if year:
                try:
                    pub_date = datetime(int(year), 1, 1)
                except:
                    pass
            
            pdf_url = result.get("eprint_url")
            source_url = result.get("pub_url") or result.get("url")
            
            paper_id = result.get("author_pub_id") or title.replace(" ", "_")[:50]
            
            return Paper(
                paper_id=f"gs_{paper_id}",
                title=title,
                authors=authors,
                abstract=abstract or "",
                publication_date=pub_date,
                source=self.get_source(),
                source_url=source_url,
                pdf_url=pdf_url,
                metadata={
                    "venue": bib.get("venue"),
                    "num_citations": result.get("num_citations", 0),
                    "citedby_url": result.get("citedby_url"),
                }
            )
        except Exception as e:
            logger.error(f"Error converting Google Scholar paper: {e}")
            return None
