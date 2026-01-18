#!/usr/bin/env python3
"""
Command-line interface for the Multi-Agent Research Analysis Platform.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import print as rprint

from config import get_settings
from extractors import ExtractionOrchestrator, PaperSource
from agents import AgentFactory, AgentOrchestrator, ConsensusEngine

app = typer.Typer(help="Multi-Agent Research Analysis Platform CLI")
console = Console()


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    max_results: int = typer.Option(10, help="Maximum papers to retrieve"),
    sources: Optional[str] = typer.Option(None, help="Comma-separated sources (arxiv,pubmed,etc)"),
    download: bool = typer.Option(True, help="Download PDFs"),
    output: Optional[Path] = typer.Option(None, help="Output JSON file")
):
    """Search for research papers across multiple sources."""
    
    async def run():
        settings = get_settings()
        extractor = ExtractionOrchestrator(
            semantic_scholar_api_key=settings.semantic_scholar_api_key,
            storage_path=settings.paper_storage_path
        )
        
        sources_list = None
        if sources:
            sources_list = [PaperSource(s.strip()) for s in sources.split(',')]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Searching for papers...", total=None)
            
            papers = await extractor.search_and_process(
                query=query,
                max_results=max_results,
                sources=sources_list,
                download_pdfs=download
            )
            
            progress.update(task, completed=True)
        
        console.print(f"\n[green]✓[/green] Found {len(papers)} papers\n")
        
        table = Table(title="Search Results")
        table.add_column("No.", style="cyan", width=4)
        table.add_column("Title", style="white")
        table.add_column("Source", style="yellow", width=20)
        table.add_column("Authors", style="blue", width=30)
        
        for i, paper in enumerate(papers, 1):
            authors = ", ".join(paper.authors[:2])
            if len(paper.authors) > 2:
                authors += f" et al."
            table.add_row(
                str(i),
                paper.title[:80] + "..." if len(paper.title) > 80 else paper.title,
                paper.source.value,
                authors
            )
        
        console.print(table)
        
        if output:
            with open(output, 'w') as f:
                json.dump([p.model_dump() for p in papers], f, indent=2, default=str)
            console.print(f"\n[green]✓[/green] Results saved to {output}")
    
    asyncio.run(run())


@app.command()
def analyze(
    query: str = typer.Argument(..., help="Search query for papers"),
    question: str = typer.Argument(..., help="Research question to analyze"),
    max_papers: int = typer.Option(10, help="Maximum papers to analyze"),
    full: bool = typer.Option(True, help="Run full WHAT/HOW/WHY analysis"),
    output: Optional[Path] = typer.Option(None, help="Output JSON file")
):
    """Analyze research papers with multi-agent system."""
    
    async def run():
        settings = get_settings()
        
        console.print(Panel.fit(
            f"[bold]Query:[/bold] {query}\n[bold]Question:[/bold] {question}",
            title="Research Analysis",
            border_style="blue"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task1 = progress.add_task("Searching papers...", total=None)
            
            extractor = ExtractionOrchestrator(
                semantic_scholar_api_key=settings.semantic_scholar_api_key,
                storage_path=settings.paper_storage_path
            )
            
            papers = await extractor.search_and_process(
                query=query,
                max_results=max_papers,
                download_pdfs=False
            )
            
            progress.update(task1, completed=True)
            
            if not papers:
                console.print("[red]✗[/red] No papers found")
                return
            
            console.print(f"[green]✓[/green] Found {len(papers)} papers\n")
            
            task2 = progress.add_task("Initializing agents...", total=None)
            
            agents = AgentFactory.create_agent_pool(
                openai_keys=settings.openai_api_keys,
                anthropic_keys=settings.anthropic_api_keys,
                google_keys=settings.google_api_keys,
                deepseek_key=settings.deepseek_api_key,
                qwen_key=settings.qwen_api_key,
                max_agents=settings.max_agents
            )
            
            progress.update(task2, completed=True)
            console.print(f"[green]✓[/green] Initialized {len(agents)} agents\n")
            
            task3 = progress.add_task("Running multi-agent analysis...", total=None)
            
            consensus_engine = ConsensusEngine(
                min_confidence=settings.min_confidence_score,
                consensus_threshold=settings.consensus_threshold
            )
            
            orchestrator = AgentOrchestrator(
                agents=agents,
                consensus_engine=consensus_engine,
                timeout=settings.agent_timeout
            )
            
            results = await orchestrator.analyze_papers_with_query(
                papers=papers,
                query=question,
                run_all_analysis_types=full
            )
            
            progress.update(task3, completed=True)
        
        console.print("\n" + "=" * 80 + "\n")
        console.print("[bold cyan]ANALYSIS RESULTS[/bold cyan]\n")
        
        for analysis_type, data in results["analysis_results"].items():
            consensus = data["consensus"]
            
            console.print(f"\n[bold yellow]{analysis_type.upper()} ANALYSIS[/bold yellow]")
            console.print(f"Confidence: [green]{consensus['confidence_score']:.1%}[/green]")
            console.print(f"Agreement: [green]{consensus['agreement_level']:.1%}[/green]\n")
            
            if consensus['key_findings']:
                console.print("[bold]Key Findings:[/bold]")
                for i, finding in enumerate(consensus['key_findings'][:5], 1):
                    console.print(f"  {i}. {finding[:150]}...")
                console.print()
            
            if consensus['recommendations']:
                console.print("[bold]Recommendations:[/bold]")
                for i, rec in enumerate(consensus['recommendations'][:3], 1):
                    console.print(f"  {i}. {rec[:150]}...")
                console.print()
        
        if output:
            with open(output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"\n[green]✓[/green] Full results saved to {output}")
    
    asyncio.run(run())


@app.command()
def agents():
    """List available agents and their status."""
    settings = get_settings()
    
    console.print(Panel.fit(
        "[bold]Agent Availability Check[/bold]",
        border_style="blue"
    ))
    
    table = Table(title="\nAPI Key Configuration")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Keys", style="yellow")
    
    table.add_row("OpenAI", "✓" if settings.openai_api_keys else "✗", str(len(settings.openai_api_keys)))
    table.add_row("Anthropic", "✓" if settings.anthropic_api_keys else "✗", str(len(settings.anthropic_api_keys)))
    table.add_row("Google", "✓" if settings.google_api_keys else "✗", str(len(settings.google_api_keys)))
    table.add_row("DeepSeek", "✓" if settings.deepseek_api_key else "✗", "1" if settings.deepseek_api_key else "0")
    table.add_row("Qwen", "✓" if settings.qwen_api_key else "✗", "1" if settings.qwen_api_key else "0")
    table.add_row("X.AI (Grok)", "✓" if settings.xai_api_key else "✗", "1" if settings.xai_api_key else "0")
    table.add_row("Yi", "✓" if settings.yi_api_key else "✗", "1" if settings.yi_api_key else "0")
    
    console.print(table)
    
    console.print("\n[bold]Creating agent pool...[/bold]")
    agent_list = AgentFactory.create_agent_pool(
        openai_keys=settings.openai_api_keys,
        anthropic_keys=settings.anthropic_api_keys,
        google_keys=settings.google_api_keys,
        deepseek_key=settings.deepseek_api_key,
        qwen_key=settings.qwen_api_key,
        xai_key=settings.xai_api_key,
        yi_key=settings.yi_api_key,
        max_agents=settings.max_agents
    )
    
    agent_table = Table(title=f"\nActive Agents ({len(agent_list)})")
    agent_table.add_column("#", style="cyan", width=3)
    agent_table.add_column("Agent Type", style="yellow", width=25)
    agent_table.add_column("Model", style="white", width=35)
    agent_table.add_column("Thinking", style="green", width=8)
    
    for i, agent in enumerate(agent_list, 1):
        agent_table.add_row(
            str(i),
            agent.agent_type.value,
            agent.config.model_name,
            "Yes" if agent.config.enable_thinking else "No"
        )
    
    console.print(agent_table)
    console.print(f"\n[green]✓[/green] {len(agent_list)}/{settings.max_agents} agents available\n")


@app.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"[bold]Multi-Agent Research Platform[/bold] v{__version__}")


if __name__ == "__main__":
    app()
