import pytest
from agents.base import AgentResponse, AgentType, AnalysisType
from agents.consensus import ConsensusEngine


@pytest.mark.asyncio
async def test_consensus_basic():
    engine = ConsensusEngine(min_confidence=0.5, consensus_threshold=0.6)
    
    responses = [
        AgentResponse(
            agent_type=AgentType.CLAUDE_3,
            response="Finding A is significant",
            reasoning_chain="Analysis shows...",
            confidence_score=0.85,
            analysis_type=AnalysisType.WHAT,
            key_claims=["Finding A", "Finding B"],
            recommendations=["Recommendation 1"]
        ),
        AgentResponse(
            agent_type=AgentType.GPT4O,
            response="Finding A is important",
            reasoning_chain="Data indicates...",
            confidence_score=0.80,
            analysis_type=AnalysisType.WHAT,
            key_claims=["Finding A", "Finding C"],
            recommendations=["Recommendation 1", "Recommendation 2"]
        ),
    ]
    
    consensus = await engine.reach_consensus(responses, AnalysisType.WHAT)
    
    assert consensus.confidence_score > 0
    assert consensus.agreement_level > 0
    assert len(consensus.key_findings) > 0
    assert "Finding A" in [f.lower() for f in consensus.key_findings]


@pytest.mark.asyncio
async def test_contradiction_detection():
    engine = ConsensusEngine()
    
    responses = [
        AgentResponse(
            agent_type=AgentType.CLAUDE_3,
            response="Test",
            reasoning_chain="Test",
            confidence_score=0.8,
            analysis_type=AnalysisType.WHAT,
            contradictions=["Issue A", "Issue B"]
        ),
        AgentResponse(
            agent_type=AgentType.GPT4O,
            response="Test",
            reasoning_chain="Test",
            confidence_score=0.8,
            analysis_type=AnalysisType.WHAT,
            contradictions=["Issue A", "Issue C"]
        ),
    ]
    
    consensus = await engine.reach_consensus(responses, AnalysisType.WHAT)
    
    assert len(consensus.contradictions) > 0


def test_agent_weight_calculation():
    engine = ConsensusEngine()
    
    responses = [
        AgentResponse(
            agent_type=AgentType.CLAUDE_3,
            response="Test",
            reasoning_chain="Test",
            confidence_score=0.9,
            analysis_type=AnalysisType.WHAT,
            key_claims=["A", "B", "C"],
            evidence=[{"e": 1}, {"e": 2}]
        ),
        AgentResponse(
            agent_type=AgentType.GPT4O,
            response="Test",
            reasoning_chain="Test",
            confidence_score=0.6,
            analysis_type=AnalysisType.WHAT,
            key_claims=["A"]
        ),
    ]
    
    weights = engine._calculate_agent_weights(responses)
    
    assert len(weights) == 2
    assert weights[0] > weights[1]
    assert abs(sum(weights) - 1.0) < 0.01
