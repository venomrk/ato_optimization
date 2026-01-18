from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from loguru import logger
import sys

from ..config import get_settings
from ..extractors import ExtractionOrchestrator, PaperSource
from ..agents import AgentFactory, AgentOrchestrator, ConsensusEngine
from ..storage import get_database, get_vector_store, get_cache_manager

logger.remove()
logger.add(sys.stderr, level="INFO")


class SearchRequest(BaseModel):
    query: str
    max_results: int = Field(default=50, le=100)
    sources: Optional[List[str]] = None
    download_pdfs: bool = True


class AnalyzeRequest(BaseModel):
    query: str
    research_question: str
    max_papers: int = Field(default=20, le=50)
    run_full_analysis: bool = True


class QueryResponse(BaseModel):
    papers_found: int
    papers_analyzed: int
    agents_used: int
    analysis_results: Dict[str, Any]
    processing_time: float


def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title="Multi-Agent Research Analysis Platform",
        description="Advanced research paper analysis using multiple reasoning models",
        version="1.0.0"
    )
    
    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    @app.on_event("startup")
    async def startup_event():
        logger.info("Starting Multi-Agent Research Platform API")
        
        app.state.database = get_database(settings.database_url)
        app.state.vector_store = get_vector_store(settings.vector_db_type)
        app.state.cache = get_cache_manager(settings.redis_url)
        
        app.state.extractor = ExtractionOrchestrator(
            semantic_scholar_api_key=settings.semantic_scholar_api_key,
            storage_path=settings.paper_storage_path
        )
        
        app.state.agents = AgentFactory.create_agent_pool(
            openai_keys=settings.openai_api_keys,
            anthropic_keys=settings.anthropic_api_keys,
            google_keys=settings.google_api_keys,
            deepseek_key=settings.deepseek_api_key,
            qwen_key=settings.qwen_api_key,
            xai_key=settings.xai_api_key,
            yi_key=settings.yi_api_key,
            max_agents=settings.max_agents
        )
        
        consensus_engine = ConsensusEngine(
            min_confidence=settings.min_confidence_score,
            consensus_threshold=settings.consensus_threshold
        )
        
        app.state.orchestrator = AgentOrchestrator(
            agents=app.state.agents,
            consensus_engine=consensus_engine,
            timeout=settings.agent_timeout
        )
        
        logger.info(f"Initialized with {len(app.state.agents)} agents")
    
    @app.get("/")
    async def root():
        return {
            "service": "Multi-Agent Research Analysis Platform",
            "version": "1.0.0",
            "status": "operational"
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "agents_available": len(app.state.agents),
            "database": "connected",
            "vector_store": "connected"
        }
    
    @app.post("/search")
    async def search_papers(request: SearchRequest):
        try:
            sources_enum = None
            if request.sources:
                sources_enum = [PaperSource(s) for s in request.sources]
            
            papers = await app.state.extractor.search_and_process(
                query=request.query,
                max_results=request.max_results,
                sources=sources_enum,
                download_pdfs=request.download_pdfs
            )
            
            for paper in papers:
                paper_dict = paper.model_dump()
                app.state.database.save_paper(paper_dict)
                
                app.state.vector_store.add_paper(
                    paper_id=paper.paper_id,
                    title=paper.title,
                    abstract=paper.abstract,
                    metadata={
                        "source": paper.source.value,
                        "doi": paper.doi,
                        "authors": paper.authors,
                    }
                )
            
            return {
                "papers_found": len(papers),
                "papers": [p.model_dump(exclude={"full_text"}) for p in papers]
            }
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/analyze", response_model=QueryResponse)
    async def analyze_research(request: AnalyzeRequest):
        try:
            import time
            start_time = time.time()
            
            cache_key = f"analysis:{request.query}:{request.research_question}"
            cached_result = app.state.cache.get(cache_key)
            if cached_result:
                logger.info("Returning cached analysis result")
                return cached_result
            
            papers = await app.state.extractor.search_and_process(
                query=request.query,
                max_results=request.max_papers,
                download_pdfs=True
            )
            
            if not papers:
                raise HTTPException(status_code=404, detail="No papers found for query")
            
            analysis_results = await app.state.orchestrator.analyze_papers_with_query(
                papers=papers,
                query=request.research_question,
                run_all_analysis_types=request.run_full_analysis
            )
            
            processing_time = time.time() - start_time
            
            response = QueryResponse(
                papers_found=len(papers),
                papers_analyzed=len(papers),
                agents_used=len(app.state.agents),
                analysis_results=analysis_results,
                processing_time=processing_time
            )
            
            app.state.database.save_analysis({
                "query": request.query,
                "papers_analyzed": len(papers),
                "agents_used": len(app.state.agents),
                "results": analysis_results,
                "confidence_score": analysis_results.get("analysis_results", {}).get("general", {}).get("consensus", {}).get("confidence_score", 0.0)
            })
            
            app.state.cache.set(cache_key, response.model_dump(), ttl=7200)
            
            return response
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/analyses")
    async def get_recent_analyses(limit: int = 10):
        try:
            analyses = app.state.database.get_recent_analyses(limit=limit)
            return {"analyses": analyses}
        except Exception as e:
            logger.error(f"Error fetching analyses: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/agents")
    async def list_agents():
        return {
            "total_agents": len(app.state.agents),
            "agents": [
                {
                    "type": agent.agent_type.value,
                    "model": agent.config.model_name
                }
                for agent in app.state.agents
            ]
        }
    
    @app.post("/papers/{paper_id}/enrich")
    async def enrich_paper(paper_id: str):
        try:
            paper_data = app.state.database.get_paper(paper_id)
            if not paper_data:
                raise HTTPException(status_code=404, detail="Paper not found")
            
            from ..extractors.base import Paper
            paper = Paper(**paper_data)
            
            from ..extractors.pdf_processor import PDFProcessor
            processor = PDFProcessor()
            enriched_paper = await processor.enrich_paper(paper)
            
            app.state.database.save_paper(enriched_paper.model_dump())
            
            return {"status": "enriched", "paper_id": paper_id}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Enrichment error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    app = create_app()
    uvicorn.run(
        app, 
        host=settings.api_host, 
        port=settings.api_port,
        workers=settings.api_workers
    )
