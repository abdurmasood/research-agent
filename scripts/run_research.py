#!/usr/bin/env python
"""
CLI script to run research queries

Usage: python scripts/run_research.py "Your research query here"
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table
from research_system.core.orchestrator import MultiAgentResearchSystem
from research_system.core.models import ProgressUpdate
from research_system.utils.formatters import save_result
from research_system.utils.logging import setup_logging
from config.settings import settings

console = Console()


def create_progress_callback(progress: Progress, task_id):
    """Create progress callback for rich progress bar"""

    def callback(update: ProgressUpdate):
        progress.update(
            task_id,
            completed=update.percent,
            description=f"[cyan]{update.message}"
        )

        # Log phase changes
        if update.phase in ['planning_complete', 'subagent_complete', 'complete']:
            console.log(f"✓ {update.message}")

    return callback


async def main():
    # Check arguments
    if len(sys.argv) < 2:
        console.print("[red]Error: Please provide a research query[/red]")
        console.print("\nUsage: python scripts/run_research.py \"Your query here\"")
        console.print("\nExample:")
        console.print("  python scripts/run_research.py \"What are the environmental impacts of electric vehicles?\"")
        sys.exit(1)

    query = " ".join(sys.argv[1:])

    # Setup logging
    setup_logging(
        log_level=settings.log_level,
        log_file=settings.log_file
    )

    # Display header
    console.print()
    console.print(Panel.fit(
        f"[bold green]Multi-Agent Research System[/bold green]\n"
        f"[dim]Powered by Claude Sonnet 4.5 & Parallel.ai[/dim]",
        border_style="green"
    ))
    console.print()
    console.print(f"[bold]Query:[/bold] {query}")
    console.print()

    # Initialize system with progress tracking
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Initializing...", total=100)
        callback = create_progress_callback(progress, task)
        system = MultiAgentResearchSystem(progress_callback=callback)

        try:
            # Run research
            result = await system.research(query)

            console.print()
            console.print("[bold green]✓ Research Complete![/bold green]")
            console.print()

            # Create summary table
            table = Table(title="Research Summary", show_header=True, header_style="bold cyan")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Subagents Used", str(result.metadata.get('subagents_count', 'N/A')))
            table.add_row("Sources Consulted", str(result.metadata.get('sources_count', 'N/A')))
            table.add_row("Duration", f"{result.metadata.get('duration_seconds', 0):.2f}s")
            table.add_row("Report Length", f"{len(result.cited_report)} characters")
            table.add_row("Citations", str(len(result.bibliography)))

            console.print(table)
            console.print()

            # Save results
            md_path, json_path, html_path = save_result(result)

            console.print("[bold]Output Files:[/bold]")
            console.print(f"  📄 Markdown: [blue]{md_path}[/blue]")
            console.print(f"  📊 JSON: [blue]{json_path}[/blue]")
            console.print(f"  🌐 HTML: [blue]{html_path}[/blue]")
            console.print()

            # Display excerpt of report
            console.print(Panel(
                result.cited_report[:500] + "..." if len(result.cited_report) > 500 else result.cited_report,
                title="[bold]Report Preview[/bold]",
                border_style="blue"
            ))

        except KeyboardInterrupt:
            console.print("\n[yellow]Research interrupted by user[/yellow]")
            sys.exit(130)

        except Exception as e:
            console.print()
            console.print(f"[bold red]Error:[/bold red] {e}")
            console.print()
            console.print("[dim]Check logs/research.log for details[/dim]")
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
