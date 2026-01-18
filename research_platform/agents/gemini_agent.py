import time
import re
from typing import List
import google.generativeai as genai
from loguru import logger
from .base import Agent, AgentResponse, AgentConfig, AnalysisType


class GeminiAgent(Agent):
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        genai.configure(api_key=config.api_key)
        self.model = genai.GenerativeModel(config.model_name)
    
    async def analyze_paper(
        self,
        paper_content: str,
        query: str,
        analysis_type: AnalysisType = AnalysisType.GENERAL
    ) -> AgentResponse:
        start_time = time.time()
        
        try:
            prompt = self._build_prompt(query, paper_content, analysis_type)
            
            generation_config = genai.GenerationConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
            )
            
            response = await self.model.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            content_text = response.text
            reasoning_text = content_text[:1000]
            
            parsed_response = self._parse_response(content_text)
            
            processing_time = time.time() - start_time
            
            return AgentResponse(
                agent_type=self.config.agent_type,
                response=content_text,
                reasoning_chain=reasoning_text,
                confidence_score=parsed_response.get("confidence", 0.75),
                analysis_type=analysis_type,
                key_claims=parsed_response.get("claims", []),
                evidence=parsed_response.get("evidence", []),
                contradictions=parsed_response.get("contradictions", []),
                recommendations=parsed_response.get("recommendations", []),
                citations=parsed_response.get("citations", []),
                processing_time=processing_time
            )
        except Exception as e:
            logger.error(f"Error in Gemini agent analysis: {e}")
            raise
    
    async def analyze_papers(
        self,
        papers_content: List[str],
        query: str,
        analysis_type: AnalysisType = AnalysisType.GENERAL
    ) -> AgentResponse:
        combined_content = "\n\n---PAPER---\n\n".join(papers_content[:5])
        return await self.analyze_paper(combined_content, query, analysis_type)
    
    def _parse_response(self, response_text: str) -> dict:
        parsed = {
            "claims": [],
            "evidence": [],
            "contradictions": [],
            "recommendations": [],
            "citations": [],
            "confidence": 0.75
        }
        
        confidence_match = re.search(r'confidence[:\s]+(\d+\.?\d*)%?', response_text, re.IGNORECASE)
        if confidence_match:
            conf_value = float(confidence_match.group(1))
            parsed["confidence"] = conf_value / 100 if conf_value > 1 else conf_value
        
        claims_section = re.search(r'(?:key claims?|findings?)[:\s]+(.+?)(?=\n\n|\z)', response_text, re.IGNORECASE | re.DOTALL)
        if claims_section:
            claims_text = claims_section.group(1)
            parsed["claims"] = [c.strip() for c in re.split(r'\n[-•\d]+\.?\s*', claims_text) if c.strip()][:10]
        
        rec_section = re.search(r'(?:recommendations?|future work)[:\s]+(.+?)(?=\n\n|\z)', response_text, re.IGNORECASE | re.DOTALL)
        if rec_section:
            rec_text = rec_section.group(1)
            parsed["recommendations"] = [r.strip() for r in re.split(r'\n[-•\d]+\.?\s*', rec_text) if r.strip()][:5]
        
        return parsed
