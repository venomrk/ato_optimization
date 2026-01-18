from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter
import numpy as np
from pydantic import BaseModel, Field
from .base import AgentResponse, AnalysisType
from loguru import logger


class ConsensusResult(BaseModel):
    consolidated_answer: str
    confidence_score: float
    agreement_level: float
    key_findings: List[str] = Field(default_factory=list)
    evidence_summary: List[Dict[str, Any]] = Field(default_factory=list)
    contradictions: List[Dict[str, Any]] = Field(default_factory=list)
    agent_votes: Dict[str, float] = Field(default_factory=dict)
    minority_opinions: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    reasoning_synthesis: str = ""


class ConsensusEngine:
    def __init__(self, min_confidence: float = 0.6, consensus_threshold: float = 0.7):
        self.min_confidence = min_confidence
        self.consensus_threshold = consensus_threshold
    
    async def reach_consensus(
        self, 
        responses: List[AgentResponse],
        analysis_type: AnalysisType
    ) -> ConsensusResult:
        if not responses:
            return ConsensusResult(
                consolidated_answer="No responses available",
                confidence_score=0.0,
                agreement_level=0.0
            )
        
        filtered_responses = [r for r in responses if r.confidence_score >= self.min_confidence]
        
        if not filtered_responses:
            logger.warning(f"No responses met minimum confidence threshold of {self.min_confidence}")
            filtered_responses = responses
        
        agent_weights = self._calculate_agent_weights(filtered_responses)
        
        key_findings = self._consolidate_findings(filtered_responses, agent_weights)
        
        contradictions = self._identify_contradictions(filtered_responses)
        
        consensus_answer = self._synthesize_answer(filtered_responses, agent_weights)
        
        recommendations = self._consolidate_recommendations(filtered_responses, agent_weights)
        
        overall_confidence = self._calculate_overall_confidence(filtered_responses, agent_weights)
        
        agreement_level = self._calculate_agreement_level(filtered_responses)
        
        minority_opinions = self._extract_minority_opinions(filtered_responses, agent_weights)
        
        reasoning_synthesis = self._synthesize_reasoning(filtered_responses)
        
        return ConsensusResult(
            consolidated_answer=consensus_answer,
            confidence_score=overall_confidence,
            agreement_level=agreement_level,
            key_findings=key_findings,
            contradictions=contradictions,
            agent_votes={str(r.agent_type.value): agent_weights[i] for i, r in enumerate(filtered_responses)},
            minority_opinions=minority_opinions,
            recommendations=recommendations,
            reasoning_synthesis=reasoning_synthesis
        )
    
    def _calculate_agent_weights(self, responses: List[AgentResponse]) -> List[float]:
        weights = []
        for response in responses:
            base_weight = response.confidence_score
            
            evidence_bonus = min(len(response.evidence) * 0.05, 0.2)
            claims_bonus = min(len(response.key_claims) * 0.03, 0.15)
            
            weight = base_weight + evidence_bonus + claims_bonus
            weights.append(min(weight, 1.0))
        
        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]
        
        return weights
    
    def _consolidate_findings(
        self, 
        responses: List[AgentResponse], 
        weights: List[float]
    ) -> List[str]:
        all_claims = []
        for response, weight in zip(responses, weights):
            for claim in response.key_claims:
                all_claims.append((claim.lower().strip(), weight))
        
        claim_scores = defaultdict(float)
        claim_originals = {}
        
        for claim, weight in all_claims:
            claim_scores[claim] += weight
            if claim not in claim_originals:
                claim_originals[claim] = claim
        
        sorted_claims = sorted(claim_scores.items(), key=lambda x: x[1], reverse=True)
        
        top_findings = []
        for claim, score in sorted_claims[:15]:
            if score >= self.consensus_threshold * max(weights):
                top_findings.append(claim_originals[claim])
        
        return top_findings
    
    def _identify_contradictions(self, responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        contradictions = []
        
        all_contradictions = []
        for response in responses:
            all_contradictions.extend(response.contradictions)
        
        contradiction_counter = Counter([c.lower() for c in all_contradictions])
        
        for contradiction, count in contradiction_counter.most_common(10):
            if count >= 2:
                contradictions.append({
                    "statement": contradiction,
                    "frequency": count,
                    "severity": "high" if count >= len(responses) * 0.5 else "medium"
                })
        
        return contradictions
    
    def _synthesize_answer(
        self, 
        responses: List[AgentResponse], 
        weights: List[float]
    ) -> str:
        weighted_responses = []
        for response, weight in zip(responses, weights):
            if weight >= self.consensus_threshold:
                weighted_responses.append(response.response)
        
        if not weighted_responses:
            weighted_responses = [r.response for r in responses[:3]]
        
        synthesis = "Based on multi-agent analysis:\n\n"
        
        for i, response_text in enumerate(weighted_responses[:5], 1):
            excerpt = response_text[:500].strip()
            synthesis += f"{i}. {excerpt}...\n\n"
        
        return synthesis
    
    def _consolidate_recommendations(
        self, 
        responses: List[AgentResponse], 
        weights: List[float]
    ) -> List[str]:
        all_recs = []
        for response, weight in zip(responses, weights):
            for rec in response.recommendations:
                all_recs.append((rec.lower().strip(), weight))
        
        rec_scores = defaultdict(float)
        rec_originals = {}
        
        for rec, weight in all_recs:
            rec_scores[rec] += weight
            if rec not in rec_originals:
                rec_originals[rec] = rec
        
        sorted_recs = sorted(rec_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [rec_originals[rec] for rec, score in sorted_recs[:10]]
    
    def _calculate_overall_confidence(
        self, 
        responses: List[AgentResponse], 
        weights: List[float]
    ) -> float:
        weighted_confidence = sum(
            r.confidence_score * w 
            for r, w in zip(responses, weights)
        )
        return round(weighted_confidence, 3)
    
    def _calculate_agreement_level(self, responses: List[AgentResponse]) -> float:
        if len(responses) < 2:
            return 1.0
        
        confidences = [r.confidence_score for r in responses]
        std_dev = np.std(confidences)
        
        agreement = 1.0 - min(std_dev, 1.0)
        
        return round(agreement, 3)
    
    def _extract_minority_opinions(
        self, 
        responses: List[AgentResponse], 
        weights: List[float]
    ) -> List[str]:
        minority = []
        
        avg_weight = np.mean(weights)
        
        for response, weight in zip(responses, weights):
            if weight < avg_weight * 0.5:
                unique_claims = [c for c in response.key_claims if c not in minority]
                minority.extend(unique_claims[:2])
        
        return minority[:5]
    
    def _synthesize_reasoning(self, responses: List[AgentResponse]) -> str:
        reasoning_chains = [r.reasoning_chain for r in responses if r.reasoning_chain]
        
        if not reasoning_chains:
            return "No detailed reasoning available."
        
        synthesis = "Synthesized reasoning from agents:\n\n"
        for i, chain in enumerate(reasoning_chains[:3], 1):
            excerpt = chain[:300].strip()
            synthesis += f"Agent {i}: {excerpt}...\n\n"
        
        return synthesis
