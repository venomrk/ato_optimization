from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AgentType(str, Enum):
    CLAUDE_3 = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    GPT4_TURBO = "gpt-4-turbo"
    GPT4O = "gpt-4o"
    O1 = "o1"
    O3 = "o3"
    QWEN_QWQ = "qwen-qwq"
    DEEPSEEK_R1 = "deepseek-r1"
    GEMINI_2 = "gemini-2.0-flash-thinking-exp"
    LLAMA_3_70B = "llama-3-70b"
    MIXTRAL_8X22B = "mixtral-8x22b"
    GROK_2 = "grok-2"
    YI_LIGHTNING = "yi-lightning"


class AnalysisType(str, Enum):
    WHAT = "what"
    HOW = "how"
    WHY = "why"
    GENERAL = "general"


class AgentConfig(BaseModel):
    agent_type: AgentType
    api_key: str
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 300
    enable_thinking: bool = True


class AgentResponse(BaseModel):
    agent_type: AgentType
    response: str
    reasoning_chain: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    analysis_type: AnalysisType
    key_claims: List[str] = Field(default_factory=list)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    citations: List[str] = Field(default_factory=list)
    processing_time: float = 0.0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Agent(ABC):
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_type = config.agent_type
    
    @abstractmethod
    async def analyze_paper(
        self,
        paper_content: str,
        query: str,
        analysis_type: AnalysisType = AnalysisType.GENERAL
    ) -> AgentResponse:
        pass
    
    @abstractmethod
    async def analyze_papers(
        self,
        papers_content: List[str],
        query: str,
        analysis_type: AnalysisType = AnalysisType.GENERAL
    ) -> AgentResponse:
        pass
    
    def _build_prompt(self, query: str, paper_content: str, analysis_type: AnalysisType) -> str:
        base_prompt = f"""You are an expert research analyst. Analyze the following research paper to answer this query: {query}

Paper Content:
{paper_content[:10000]}

Please provide a comprehensive analysis focusing on the {analysis_type.value.upper()} aspect:
"""
        
        if analysis_type == AnalysisType.WHAT:
            base_prompt += """
- WHAT are the key findings and results?
- WHAT materials/methods were used?
- WHAT measurements were reported?
- WHAT are the main conclusions?
"""
        elif analysis_type == AnalysisType.HOW:
            base_prompt += """
- HOW were the experiments conducted?
- HOW were the materials prepared?
- HOW were the measurements performed?
- HOW did the methodology lead to the results?
"""
        elif analysis_type == AnalysisType.WHY:
            base_prompt += """
- WHY were these specific methods chosen?
- WHY do the results occur (underlying mechanisms)?
- WHY are these findings significant?
- WHY might there be limitations or contradictions?
"""
        
        base_prompt += """
For your response, structure it as follows:
1. Direct answer to the query
2. Key claims with evidence
3. Confidence score (0-1) for each claim
4. Supporting citations from the paper
5. Any contradictions or uncertainties
6. Recommendations for future work

Show your reasoning chain and explain how you arrived at your conclusions.
"""
        return base_prompt
    
    def _build_multi_paper_prompt(
        self, 
        query: str, 
        papers_content: List[str], 
        analysis_type: AnalysisType
    ) -> str:
        papers_text = "\n\n---PAPER SEPARATOR---\n\n".join([p[:5000] for p in papers_content[:10]])
        
        base_prompt = f"""You are an expert research analyst. Analyze the following research papers to answer this query: {query}

Papers Content (separated by ---PAPER SEPARATOR---):
{papers_text}

Please provide a comprehensive cross-paper analysis focusing on the {analysis_type.value.upper()} aspect:
"""
        
        if analysis_type == AnalysisType.WHAT:
            base_prompt += """
- WHAT are the consistent findings across papers?
- WHAT materials/methods are commonly used?
- WHAT are the key differences in results?
- WHAT consensus exists in the literature?
"""
        elif analysis_type == AnalysisType.HOW:
            base_prompt += """
- HOW do methodologies compare across papers?
- HOW do different approaches affect outcomes?
- HOW can the methods be synthesized?
- HOW reproducible are the results?
"""
        elif analysis_type == AnalysisType.WHY:
            base_prompt += """
- WHY do different papers reach different conclusions?
- WHY are certain approaches more effective?
- WHY do mechanisms vary across studies?
- WHY are there contradictions in the literature?
"""
        
        base_prompt += """
For your response:
1. Synthesize findings across all papers
2. Identify agreements and contradictions
3. Provide confidence scores
4. Cross-reference between papers
5. Highlight gaps in knowledge
6. Recommend research directions

Show detailed reasoning for your synthesis.
"""
        return base_prompt
