from pymed import PubMed
from typing import List, Optional
from datetime import datetime
import httpx
from loguru import logger
from .base import PaperExtractor, Paper, PaperSource


class PubMedExtractor(PaperExtractor):
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(api_key)
        self.pubmed = PubMed(tool="ResearchPlatform", email="research@platform.ai")
    
    def get_source(self) -> PaperSource:
        return PaperSource.PUBMED
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        try:
            results = self.pubmed.query(query, max_results=max_results)
            papers = []
            
            for article in results:
                paper = self._convert_to_paper(article)
                if paper:
                    papers.append(paper)
            
            logger.info(f"Found {len(papers)} papers from PubMed for query: {query}")
            return papers
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            return []
    
    async def get_paper(self, paper_id: str) -> Optional[Paper]:
        try:
            results = self.pubmed.query(paper_id, max_results=1)
            article = next(results, None)
            if article:
                return self._convert_to_paper(article)
            return None
        except Exception as e:
            logger.error(f"Error fetching PubMed paper {paper_id}: {e}")
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
    
    def _convert_to_paper(self, article) -> Optional[Paper]:
        try:
            pubmed_id = article.pubmed_id.strip() if hasattr(article, 'pubmed_id') else None
            if not pubmed_id:
                return None
            
            title = article.title if hasattr(article, 'title') else ""
            abstract = article.abstract if hasattr(article, 'abstract') else ""
            
            authors = []
            if hasattr(article, 'authors'):
                authors = [f"{a.get('lastname', '')} {a.get('firstname', '')}".strip() 
                          for a in article.authors if isinstance(a, dict)]
            
            pub_date = None
            if hasattr(article, 'publication_date'):
                try:
                    pub_date = article.publication_date
                    if isinstance(pub_date, str):
                        pub_date = datetime.fromisoformat(pub_date)
                except:
                    pass
            
            doi = article.doi if hasattr(article, 'doi') else None
            
            pdf_url = None
            if doi:
                pdf_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{doi}/pdf/"
            
            return Paper(
                paper_id=f"pubmed_{pubmed_id}",
                title=title,
                authors=authors,
                abstract=abstract or "",
                publication_date=pub_date,
                source=self.get_source(),
                source_url=f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/",
                pdf_url=pdf_url,
                doi=doi,
                metadata={
                    "pubmed_id": pubmed_id,
                    "journal": getattr(article, 'journal', None),
                    "methods": getattr(article, 'methods', None),
                }
            )
        except Exception as e:
            logger.error(f"Error converting PubMed article: {e}")
            return None
