import asyncio
from typing import List, Dict, Any
from loguru import logger
from .base import Agent, AgentResponse, AnalysisType
from .consensus import ConsensusEngine, ConsensusResult
from ..extractors.base import Paper


class AgentOrchestrator:
    def __init__(
        self, 
        agents: List[Agent],
        consensus_engine: ConsensusEngine,
        timeout: int = 300
    ):
        self.agents = agents
        self.consensus_engine = consensus_engine
        self.timeout = timeout
    
    async def analyze_papers_with_query(
        self,
        papers: List[Paper],
        query: str,
        run_all_analysis_types: bool = True
    ) -> Dict[str, Any]:
        logger.info(f"Starting multi-agent analysis with {len(self.agents)} agents on {len(papers)} papers")
        
        paper_contents = []
        for paper in papers:
            content = f"Title: {paper.title}\n\nAuthors: {', '.join(paper.authors)}\n\nAbstract: {paper.abstract}\n\n"
            if paper.full_text:
                content += f"Full Text (excerpt): {paper.full_text[:5000]}\n\n"
            if paper.key_findings:
                content += f"Key Findings: {'; '.join(paper.key_findings)}\n\n"
            paper_contents.append(content)
        
        results = {}
        
        if run_all_analysis_types:
            analysis_types = [AnalysisType.WHAT, AnalysisType.HOW, AnalysisType.WHY, AnalysisType.GENERAL]
        else:
            analysis_types = [AnalysisType.GENERAL]
        
        for analysis_type in analysis_types:
            logger.info(f"Running {analysis_type.value} analysis...")
            
            responses = await self._run_agents(paper_contents, query, analysis_type)
            
            consensus = await self.consensus_engine.reach_consensus(responses, analysis_type)
            
            results[analysis_type.value] = {
                "agent_responses": [self._response_to_dict(r) for r in responses],
                "consensus": self._consensus_to_dict(consensus)
            }
        
        return {
            "query": query,
            "papers_analyzed": len(papers),
            "agents_used": len(self.agents),
            "analysis_results": results
        }
    
    async def _run_agents(
        self,
        paper_contents: List[str],
        query: str,
        analysis_type: AnalysisType
    ) -> List[AgentResponse]:
        tasks = []
        for agent in self.agents:
            task = asyncio.create_task(
                self._run_agent_with_timeout(agent, paper_contents, query, analysis_type)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_responses = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Agent {self.agents[i].agent_type} failed: {result}")
            elif result is not None:
                successful_responses.append(result)
        
        logger.info(f"Completed analysis with {len(successful_responses)}/{len(self.agents)} agents")
        return successful_responses
    
    async def _run_agent_with_timeout(
        self,
        agent: Agent,
        paper_contents: List[str],
        query: str,
        analysis_type: AnalysisType
    ) -> AgentResponse:
        try:
            response = await asyncio.wait_for(
                agent.analyze_papers(paper_contents, query, analysis_type),
                timeout=self.timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.error(f"Agent {agent.agent_type} timed out after {self.timeout}s")
            raise
        except Exception as e:
            logger.error(f"Agent {agent.agent_type} error: {e}")
            raise
    
    def _response_to_dict(self, response: AgentResponse) -> Dict[str, Any]:
        return {
            "agent_type": response.agent_type.value,
            "response": response.response,
            "reasoning_chain": response.reasoning_chain,
            "confidence_score": response.confidence_score,
            "analysis_type": response.analysis_type.value,
            "key_claims": response.key_claims,
            "evidence": response.evidence,
            "contradictions": response.contradictions,
            "recommendations": response.recommendations,
            "citations": response.citations,
            "processing_time": response.processing_time,
            "timestamp": response.timestamp.isoformat()
        }
    
    def _consensus_to_dict(self, consensus: ConsensusResult) -> Dict[str, Any]:
        return {
            "consolidated_answer": consensus.consolidated_answer,
            "confidence_score": consensus.confidence_score,
            "agreement_level": consensus.agreement_level,
            "key_findings": consensus.key_findings,
            "contradictions": consensus.contradictions,
            "agent_votes": consensus.agent_votes,
            "minority_opinions": consensus.minority_opinions,
            "recommendations": consensus.recommendations,
            "reasoning_synthesis": consensus.reasoning_synthesis
        }
