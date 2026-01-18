# Usage Examples

## Example 1: Material Science Research

### Query: Transparent Conducting Oxides

**Research Question**: What are the optimal processing parameters for antimony-fluorine co-doped tin oxide to maximize both electrical conductivity and optical transparency?

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "antimony fluorine doped tin oxide transparent conducting",
    "research_question": "What are the optimal processing parameters for AFTO to maximize conductivity and transparency?",
    "max_papers": 20,
    "run_full_analysis": true
  }'
```

**Expected Output**:
- **WHAT Analysis**: Key findings on doping concentrations, sheet resistance values, transmittance percentages
- **HOW Analysis**: Deposition methods (spray pyrolysis, sputtering), annealing conditions, substrate preparation
- **WHY Analysis**: Mechanisms of conductivity enhancement, transparency-conductivity trade-offs, dopant interactions

## Example 2: AI/Machine Learning

### Query: Transformer Attention Mechanisms

**Research Question**: How do different attention mechanisms (multi-head, sparse, linear) affect model performance on long-sequence tasks?

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "transformer attention mechanisms long sequences",
    "research_question": "How do different attention mechanisms affect performance on long sequences?",
    "max_papers": 15,
    "run_full_analysis": true
  }'
```

**Key Findings Might Include**:
- Sparse attention reduces computational complexity from O(n²) to O(n log n)
- Linear attention maintains performance up to 8K tokens
- Multi-head attention provides better representation diversity
- Trade-offs between speed, memory, and accuracy

## Example 3: Biomedical Research

### Query: mRNA Vaccine Delivery

**Research Question**: Why are lipid nanoparticles effective for mRNA delivery and what are the current limitations?

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "lipid nanoparticles mRNA vaccine delivery",
    "research_question": "Why are LNPs effective for mRNA delivery and what are the limitations?",
    "max_papers": 15,
    "run_full_analysis": true
  }'
```

**Analysis Might Cover**:
- Mechanisms: Endosomal escape, protection from RNases, cellular uptake
- Effectiveness: >90% encapsulation efficiency, organ targeting
- Limitations: Stability, storage requirements, immunogenicity concerns
- Future directions: Next-generation lipids, targeted delivery

## Example 4: Energy Storage

### Query: Solid-State Batteries

**Research Question**: What materials show the most promise for solid electrolytes in lithium batteries and why?

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "solid state electrolytes lithium batteries",
    "research_question": "What solid electrolyte materials are most promising and why?",
    "max_papers": 20,
    "run_full_analysis": true
  }'
```

## Example 5: Quantum Computing

### Query: Error Correction Codes

**Research Question**: What quantum error correction codes are most practical for near-term quantum computers?

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quantum error correction codes NISQ",
    "research_question": "Which error correction codes are most practical for NISQ devices?",
    "max_papers": 15,
    "run_full_analysis": true
  }'
```

## Python Client Examples

### Example 1: Search and Save Papers

```python
import httpx
import asyncio
import json

async def search_papers():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/search",
            json={
                "query": "graphene oxide synthesis",
                "max_results": 20,
                "sources": ["arxiv", "semantic_scholar"],
                "download_pdfs": True
            },
            timeout=120.0
        )
        
        data = response.json()
        print(f"Found {data['papers_found']} papers")
        
        with open("papers.json", "w") as f:
            json.dump(data, f, indent=2)

asyncio.run(search_papers())
```

### Example 2: Multi-Stage Analysis

```python
import httpx
import asyncio

async def comprehensive_analysis():
    async with httpx.AsyncClient(timeout=600.0) as client:
        # Step 1: Search for papers
        search_response = await client.post(
            "http://localhost:8000/search",
            json={
                "query": "perovskite solar cells stability",
                "max_results": 25,
                "download_pdfs": False
            }
        )
        papers = search_response.json()
        print(f"Found {papers['papers_found']} papers")
        
        # Step 2: Analyze WHAT
        what_response = await client.post(
            "http://localhost:8000/analyze",
            json={
                "query": "perovskite solar cells",
                "research_question": "What factors affect perovskite solar cell stability?",
                "max_papers": 15,
                "run_full_analysis": False  # Only general analysis
            }
        )
        what_results = what_response.json()
        
        print("\nWHAT Analysis:")
        consensus = what_results['analysis_results']['general']['consensus']
        print(f"Confidence: {consensus['confidence_score']:.1%}")
        for finding in consensus['key_findings'][:5]:
            print(f"- {finding}")
        
        # Step 3: Analyze HOW
        how_response = await client.post(
            "http://localhost:8000/analyze",
            json={
                "query": "perovskite solar cells",
                "research_question": "How are stable perovskite solar cells fabricated?",
                "max_papers": 15,
                "run_full_analysis": True
            }
        )
        how_results = how_response.json()
        
        print("\nHOW Analysis:")
        how_consensus = how_results['analysis_results']['how']['consensus']
        for rec in how_consensus['recommendations'][:3]:
            print(f"- {rec}")

asyncio.run(comprehensive_analysis())
```

### Example 3: Batch Processing

```python
import httpx
import asyncio
from typing import List

async def batch_analyze(queries: List[dict]):
    async with httpx.AsyncClient(timeout=600.0) as client:
        tasks = []
        for query_data in queries:
            task = client.post(
                "http://localhost:8000/analyze",
                json=query_data
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                print(f"Query {i+1} failed: {response}")
            else:
                results.append(response.json())
        
        return results

queries = [
    {
        "query": "2D materials synthesis",
        "research_question": "What are the most scalable synthesis methods for 2D materials?",
        "max_papers": 10,
        "run_full_analysis": False
    },
    {
        "query": "neuromorphic computing",
        "research_question": "What hardware architectures are most energy-efficient for neuromorphic computing?",
        "max_papers": 10,
        "run_full_analysis": False
    }
]

results = asyncio.run(batch_analyze(queries))
print(f"Completed {len(results)} analyses")
```

### Example 4: Monitoring Agent Performance

```python
import httpx
import asyncio

async def monitor_agents():
    async with httpx.AsyncClient() as client:
        # Check agent status
        agents_response = await client.get("http://localhost:8000/agents")
        agents = agents_response.json()
        
        print(f"Total Agents: {agents['total_agents']}")
        print("\nAgent Types:")
        for agent in agents['agents']:
            print(f"  - {agent['type']}: {agent['model']}")
        
        # Check recent analyses
        analyses_response = await client.get("http://localhost:8000/analyses?limit=5")
        analyses = analyses_response.json()
        
        print(f"\nRecent Analyses: {len(analyses['analyses'])}")
        for analysis in analyses['analyses']:
            print(f"  - Query: {analysis['query'][:60]}...")
            print(f"    Confidence: {analysis['confidence_score']:.1%}")
            print(f"    Papers: {analysis['papers_analyzed']}")

asyncio.run(monitor_agents())
```

## CLI Examples

### Search Papers

```bash
# Basic search
python cli.py search "carbon nanotubes" --max-results=15

# With specific sources
python cli.py search "quantum dots" --sources="arxiv,semantic_scholar" --max-results=20

# Save to file
python cli.py search "machine learning" --output=papers.json
```

### Analyze Research

```bash
# Full analysis
python cli.py analyze \
  "transparent conducting oxides" \
  "What doping strategies improve conductivity?" \
  --max-papers=15 \
  --full

# Quick analysis
python cli.py analyze \
  "battery cathodes" \
  "Which cathode materials have highest capacity?" \
  --max-papers=10 \
  --no-full

# Save results
python cli.py analyze \
  "gene editing" \
  "What are the accuracy rates of CRISPR variants?" \
  --output=results.json
```

### Check Agents

```bash
python cli.py agents
```

## Makefile Examples

```bash
# Quick search
make cli-search QUERY="solar cells efficiency"

# Analysis
make cli-analyze QUERY="neural networks" QUESTION="What activation functions work best?"

# Check agent status
make check-agents

# Run example
make example

# Start platform
make docker-up

# View logs
make docker-logs
```

## Advanced Use Cases

### Case 1: Literature Survey

Automatically survey a research area:

```python
import httpx
import asyncio

async def literature_survey(topic: str, subtopics: List[str]):
    async with httpx.AsyncClient(timeout=600.0) as client:
        results = {}
        
        for subtopic in subtopics:
            response = await client.post(
                "http://localhost:8000/analyze",
                json={
                    "query": f"{topic} {subtopic}",
                    "research_question": f"What are the latest findings on {subtopic} in {topic}?",
                    "max_papers": 20,
                    "run_full_analysis": True
                }
            )
            results[subtopic] = response.json()
        
        return results

topic = "transparent conducting oxides"
subtopics = ["doping strategies", "deposition methods", "optical properties", "electrical properties"]

survey = asyncio.run(literature_survey(topic, subtopics))
```

### Case 2: Trend Analysis

Track research trends over time:

```python
async def trend_analysis(query: str, years: List[int]):
    async with httpx.AsyncClient(timeout=600.0) as client:
        trends = {}
        
        for year in years:
            response = await client.post(
                "http://localhost:8000/search",
                json={
                    "query": f"{query} year:{year}",
                    "max_results": 50
                }
            )
            trends[year] = response.json()['papers_found']
        
        return trends
```

### Case 3: Comparative Analysis

Compare different approaches:

```python
async def compare_methods(methods: List[str], context: str):
    async with httpx.AsyncClient(timeout=600.0) as client:
        comparisons = {}
        
        for method in methods:
            response = await client.post(
                "http://localhost:8000/analyze",
                json={
                    "query": f"{method} {context}",
                    "research_question": f"What are the advantages and limitations of {method}?",
                    "max_papers": 15,
                    "run_full_analysis": True
                }
            )
            comparisons[method] = response.json()
        
        return comparisons

methods = ["spray pyrolysis", "sputtering", "chemical vapor deposition"]
context = "transparent conducting oxide films"

comparison = asyncio.run(compare_methods(methods, context))
```

## Output Processing

### Extract Key Information

```python
def extract_consensus(results: dict) -> dict:
    """Extract consensus from analysis results."""
    summary = {}
    
    for analysis_type, data in results['analysis_results'].items():
        consensus = data['consensus']
        summary[analysis_type] = {
            'confidence': consensus['confidence_score'],
            'agreement': consensus['agreement_level'],
            'top_findings': consensus['key_findings'][:3],
            'recommendations': consensus['recommendations'][:3]
        }
    
    return summary
```

### Generate Report

```python
def generate_markdown_report(results: dict) -> str:
    """Generate a markdown report from results."""
    report = f"# Research Analysis Report\n\n"
    report += f"**Query**: {results['query']}\n\n"
    report += f"**Papers Analyzed**: {results['papers_analyzed']}\n\n"
    report += f"**Agents Used**: {results['agents_used']}\n\n"
    
    for analysis_type, data in results['analysis_results'].items():
        consensus = data['consensus']
        report += f"## {analysis_type.upper()} Analysis\n\n"
        report += f"- **Confidence**: {consensus['confidence_score']:.1%}\n"
        report += f"- **Agreement**: {consensus['agreement_level']:.1%}\n\n"
        
        report += "### Key Findings\n\n"
        for i, finding in enumerate(consensus['key_findings'][:5], 1):
            report += f"{i}. {finding}\n"
        report += "\n"
        
        report += "### Recommendations\n\n"
        for i, rec in enumerate(consensus['recommendations'][:3], 1):
            report += f"{i}. {rec}\n"
        report += "\n"
    
    return report
```

## Tips & Best Practices

1. **Start Small**: Begin with 5-10 papers for quick testing
2. **Use Caching**: Identical queries are cached for 2 hours
3. **Specific Questions**: More specific research questions yield better results
4. **Check Confidence**: Review consensus confidence scores
5. **Multiple Analyses**: Run WHAT/HOW/WHY separately for detailed insights
6. **Agent Diversity**: Use multiple API providers for better consensus
7. **Rate Limiting**: Be mindful of API rate limits
8. **PDF Downloads**: Enable for full-text analysis when available
