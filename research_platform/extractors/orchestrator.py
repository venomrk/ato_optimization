from typing import List, Optional, Set
from pathlib import Path
import asyncio
from loguru import logger
from .base import Paper, PaperSource
from .arxiv_extractor import ArxivExtractor
from .pubmed_extractor import PubMedExtractor
from .semantic_scholar_extractor import SemanticScholarExtractor
from .crossref_extractor import CrossRefExtractor
from .google_scholar_extractor import GoogleScholarExtractor
from .pdf_processor import PDFProcessor


class ExtractionOrchestrator:
    def __init__(
        self,
        semantic_scholar_api_key: Optional[str] = None,
        storage_path: str = "./data/papers"
    ):
        self.extractors = {
            PaperSource.ARXIV: ArxivExtractor(),
            PaperSource.PUBMED: PubMedExtractor(),
            PaperSource.SEMANTIC_SCHOLAR: SemanticScholarExtractor(semantic_scholar_api_key),
            PaperSource.CROSSREF: CrossRefExtractor(),
            PaperSource.GOOGLE_SCHOLAR: GoogleScholarExtractor(),
        }
        self.pdf_processor = PDFProcessor()
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def search_all_sources(
        self, 
        query: str, 
        max_results_per_source: int = 10,
        sources: Optional[List[PaperSource]] = None
    ) -> List[Paper]:
        if sources is None:
            sources = list(self.extractors.keys())
        
        tasks = []
        for source in sources:
            if source in self.extractors:
                extractor = self.extractors[source]
                tasks.append(extractor.search(query, max_results_per_source))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_papers = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Extractor error: {result}")
                continue
            all_papers.extend(result)
        
        deduplicated = self._deduplicate_papers(all_papers)
        
        logger.info(f"Found {len(deduplicated)} unique papers from {len(sources)} sources")
        return deduplicated
    
    async def download_and_process_paper(self, paper: Paper) -> Paper:
        if paper.source not in self.extractors:
            logger.warning(f"No extractor for source {paper.source}")
            return paper
        
        extractor = self.extractors[paper.source]
        
        pdf_filename = f"{paper.paper_id.replace('/', '_')}.pdf"
        pdf_path = self.storage_path / pdf_filename
        
        if not pdf_path.exists() and paper.pdf_url:
            success = await extractor.download_pdf(paper, str(pdf_path))
            if success:
                paper.pdf_path = str(pdf_path)
        elif pdf_path.exists():
            paper.pdf_path = str(pdf_path)
        
        if paper.pdf_path:
            paper = await self.pdf_processor.enrich_paper(paper)
        
        return paper
    
    async def search_and_process(
        self,
        query: str,
        max_results: int = 50,
        sources: Optional[List[PaperSource]] = None,
        download_pdfs: bool = True
    ) -> List[Paper]:
        papers = await self.search_all_sources(
            query,
            max_results_per_source=max_results // len(sources or self.extractors),
            sources=sources
        )
        
        papers = papers[:max_results]
        
        if download_pdfs:
            logger.info(f"Processing {len(papers)} papers...")
            tasks = [self.download_and_process_paper(paper) for paper in papers]
            papers = await asyncio.gather(*tasks)
        
        return papers
    
    def _deduplicate_papers(self, papers: List[Paper]) -> List[Paper]:
        seen_titles = set()
        seen_dois = set()
        unique_papers = []
        
        for paper in papers:
            title_normalized = paper.title.lower().strip()
            
            if paper.doi and paper.doi in seen_dois:
                continue
            
            if title_normalized in seen_titles:
                continue
            
            if paper.doi:
                seen_dois.add(paper.doi)
            seen_titles.add(title_normalized)
            unique_papers.append(paper)
        
        return unique_papers
