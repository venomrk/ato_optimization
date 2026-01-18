import pytest
from extractors import ArxivExtractor, SemanticScholarExtractor, ExtractionOrchestrator


@pytest.mark.asyncio
async def test_arxiv_search():
    extractor = ArxivExtractor()
    papers = await extractor.search("machine learning", max_results=5)
    
    assert len(papers) > 0
    assert all(p.title for p in papers)
    assert all(p.abstract for p in papers)
    assert all(p.authors for p in papers)


@pytest.mark.asyncio
async def test_semantic_scholar_search():
    extractor = SemanticScholarExtractor()
    papers = await extractor.search("quantum computing", max_results=5)
    
    assert len(papers) > 0
    for paper in papers:
        assert paper.title
        assert paper.source.value == "semantic_scholar"


@pytest.mark.asyncio
async def test_orchestrator_multi_source():
    orchestrator = ExtractionOrchestrator()
    papers = await orchestrator.search_all_sources(
        query="neural networks",
        max_results_per_source=3
    )
    
    assert len(papers) > 0
    sources = set(p.source for p in papers)
    assert len(sources) >= 2


@pytest.mark.asyncio
async def test_deduplication():
    orchestrator = ExtractionOrchestrator()
    
    from extractors.base import Paper, PaperSource
    from datetime import datetime
    
    papers = [
        Paper(
            paper_id="1",
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
            source=PaperSource.ARXIV,
            doi="10.1234/test"
        ),
        Paper(
            paper_id="2",
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
            source=PaperSource.SEMANTIC_SCHOLAR,
            doi="10.1234/test"
        ),
        Paper(
            paper_id="3",
            title="Different Paper",
            authors=["Author"],
            abstract="Abstract",
            source=PaperSource.ARXIV
        )
    ]
    
    unique = orchestrator._deduplicate_papers(papers)
    assert len(unique) == 2
