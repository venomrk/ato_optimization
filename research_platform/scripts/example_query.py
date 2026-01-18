#!/usr/bin/env python3
"""
Example script demonstrating the multi-agent research analysis platform.
Shows WHAT, HOW, WHY analysis of research papers.
"""

import asyncio
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_settings
from extractors import ExtractionOrchestrator, PaperSource
from agents import AgentFactory, AgentOrchestrator, ConsensusEngine


async def main():
    print("=" * 80)
    print("Multi-Agent Research Analysis Platform - Example Query")
    print("=" * 80)
    print()
    
    settings = get_settings()
    
    print("Step 1: Searching for papers...")
    extractor = ExtractionOrchestrator(
        semantic_scholar_api_key=settings.semantic_scholar_api_key,
        storage_path=settings.paper_storage_path
    )
    
    query = "antimony fluorine doped tin oxide transparent conducting"
    papers = await extractor.search_and_process(
        query=query,
        max_results=5,
        sources=[PaperSource.ARXIV, PaperSource.SEMANTIC_SCHOLAR],
        download_pdfs=False
    )
    
    print(f"✓ Found {len(papers)} papers")
    for i, paper in enumerate(papers, 1):
        print(f"  {i}. {paper.title[:80]}...")
    print()
    
    print("Step 2: Initializing agents...")
    agents = AgentFactory.create_agent_pool(
        openai_keys=settings.openai_api_keys,
        anthropic_keys=settings.anthropic_api_keys,
        google_keys=settings.google_api_keys,
        deepseek_key=settings.deepseek_api_key,
        qwen_key=settings.qwen_api_key,
        max_agents=10
    )
    
    print(f"✓ Activated {len(agents)} agents:")
    for agent in agents:
        print(f"  - {agent.agent_type.value} ({agent.config.model_name})")
    print()
    
    print("Step 3: Running multi-agent analysis...")
    consensus_engine = ConsensusEngine(
        min_confidence=settings.min_confidence_score,
        consensus_threshold=settings.consensus_threshold
    )
    
    orchestrator = AgentOrchestrator(
        agents=agents,
        consensus_engine=consensus_engine,
        timeout=settings.agent_timeout
    )
    
    research_question = (
        "What are the optimal doping concentrations and processing parameters "
        "for antimony-fluorine co-doped tin oxide to achieve high electrical "
        "conductivity while maintaining optical transparency?"
    )
    
    print(f"Research Question: {research_question}")
    print()
    
    results = await orchestrator.analyze_papers_with_query(
        papers=papers,
        query=research_question,
        run_all_analysis_types=True
    )
    
    print("=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)
    print()
    
    for analysis_type, data in results["analysis_results"].items():
        print(f"\n{'=' * 80}")
        print(f"{analysis_type.upper()} ANALYSIS")
        print('=' * 80)
        
        consensus = data["consensus"]
        
        print(f"\nConfidence Score: {consensus['confidence_score']:.2%}")
        print(f"Agreement Level: {consensus['agreement_level']:.2%}")
        
        print(f"\nKey Findings ({len(consensus['key_findings'])}):")
        for i, finding in enumerate(consensus['key_findings'][:5], 1):
            print(f"  {i}. {finding[:200]}...")
        
        print(f"\nRecommendations ({len(consensus['recommendations'])}):")
        for i, rec in enumerate(consensus['recommendations'][:3], 1):
            print(f"  {i}. {rec[:200]}...")
        
        if consensus['contradictions']:
            print(f"\nContradictions Detected ({len(consensus['contradictions'])}):")
            for i, contradiction in enumerate(consensus['contradictions'][:2], 1):
                print(f"  {i}. {contradiction}")
        
        print(f"\nAgent Votes:")
        for agent_type, vote in list(consensus['agent_votes'].items())[:5]:
            print(f"  {agent_type}: {vote:.3f}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Papers Analyzed: {results['papers_analyzed']}")
    print(f"Agents Used: {results['agents_used']}")
    print(f"Analysis Types: {len(results['analysis_results'])}")
    
    output_file = Path("example_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nFull results saved to: {output_file}")
    print()


if __name__ == "__main__":
    asyncio.run(main())
