import arxiv
from typing import List, Optional
from datetime import datetime
import httpx
from loguru import logger
from .base import PaperExtractor, Paper, PaperSource


class ArxivExtractor(PaperExtractor):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.client = arxiv.Client()
    
    def get_source(self) -> PaperSource:
        return PaperSource.ARXIV
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers = []
            for result in self.client.results(search):
                paper = self._convert_to_paper(result)
                papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers from arXiv for query: {query}")
            return papers
        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []
    
    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        try:
            search = arxiv.Search(id_list=[paper_id])
            result = next(self.client.results(search))
            return self._convert_to_paper(result)
        except Exception as e:
            logger.error(f"Error fetching arXiv paper {paper_id}: {e}")
            return None
    
    async def download_pdf(self, paper: Paper, output_path: str) -> bool:
        try:
            if not paper.pdf_url:
                return False
            
            async with httpx.AsyncClient() as client:
                response = await client.get(paper.pdf_url, follow_redirects=True)
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Downloaded PDF for {paper.paper_id} to {output_path}")
                return True
        except Exception as e:
            logger.error(f"Error downloading PDF for {paper.paper_id}: {e}")
            return False
    
    def _convert_to_paper(self, result: arxiv.Result) -> Paper:
        return Paper(
            paper_id=result.entry_id.split('/')[-1],
            title=result.title,
            authors=[author.name for author in result.authors],
            abstract=result.summary,
            publication_date=result.published,
            source=self.get_source(),
            source_url=result.entry_id,
            pdf_url=result.pdf_url,
            doi=result.doi,
            metadata={
                "categories": result.categories,
                "primary_category": result.primary_category,
                "comment": result.comment,
                "journal_ref": result.journal_ref,
            }
        )
