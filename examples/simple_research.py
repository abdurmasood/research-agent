"""
Simple usage example for the multi-agent research system
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from research_system.core.orchestrator import MultiAgentResearchSystem
from research_system.utils.logging import setup_logging


def print_progress(update):
    """Simple progress callback"""
    print(f"[{update.percent}%] {update.message}")


async def main():
    # Setup logging
    setup_logging()

    # Initialize system
    print("\nInitializing Multi-Agent Research System...")
    system = MultiAgentResearchSystem(progress_callback=print_progress)

    # Run research
    query = "What are the environmental impacts of electric vehicles?"
    print(f"\nResearching: {query}\n")
    print("=" * 80)

    result = await system.research(query)

    # Display results
    print("\n" + "=" * 80)
    print("RESEARCH COMPLETE")
    print("=" * 80 + "\n")

    print("CITED REPORT:")
    print("-" * 80)
    print(result.cited_report)
    print("-" * 80)

    print(f"\nMETADATA:")
    print(f"  - Subagents used: {result.metadata['subagents_count']}")
    print(f"  - Sources consulted: {result.metadata['sources_count']}")
    print(f"  - Duration: {result.metadata['duration_seconds']:.2f} seconds")
    print(f"  - Citations: {len(result.bibliography)}")

    print("\nBIBLIOGRAPHY:")
    for citation in result.bibliography[:5]:  # Show first 5
        print(f"  [{citation.index}] {citation.url}")
    if len(result.bibliography) > 5:
        print(f"  ... and {len(result.bibliography) - 5} more")

    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
