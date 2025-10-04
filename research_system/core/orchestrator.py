import asyncio
from typing import List, Callable, Optional
from langchain_anthropic import ChatAnthropic
from research_system.agents.lead_researcher import LeadResearcher
from research_system.agents.subagent import ResearchSubagent
from research_system.agents.citation_agent import CitationAgent
from research_system.tools.parallel_search import get_parallel_search_tool
from research_system.core.models import ResearchResult, ProgressUpdate
from research_system.utils.logging import get_logger
from config.settings import settings
import time

logger = get_logger(__name__)


class MultiAgentResearchSystem:
    """Main orchestrator for multi-agent research"""

    def __init__(self, progress_callback: Optional[Callable] = None):
        """
        Initialize multi-agent research system

        Args:
            progress_callback: Optional callback function for progress updates
        """
        # Initialize Claude LLM
        self.llm = ChatAnthropic(
            model=settings.model_name,
            api_key=settings.anthropic_api_key,
            temperature=settings.model_temperature,
            max_tokens=settings.max_tokens
        )

        # Initialize tools
        self.tools = [get_parallel_search_tool()]

        # Initialize agents
        self.lead_researcher = LeadResearcher(self.llm)
        self.citation_agent = CitationAgent(self.llm)

        # Progress callback
        self.progress_callback = progress_callback or self._default_callback

    def _default_callback(self, update: ProgressUpdate):
        """Default progress callback - just log"""
        logger.info(f"[{update.percent}%] {update.message}")

    def _send_progress(self, phase: str, message: str, percent: int, **details):
        """Send progress update via callback"""
        update = ProgressUpdate(
            phase=phase,
            message=message,
            percent=percent,
            details=details if details else None
        )
        self.progress_callback(update)

    async def research(self, query: str) -> ResearchResult:
        """
        Execute full multi-agent research workflow

        Args:
            query: Research query string

        Returns:
            ResearchResult with complete findings
        """
        logger.info(f"Starting research for query: {query}")
        start_time = time.time()

        try:
            # Step 1: Create research plan
            self._send_progress(
                'planning',
                'Analyzing query and creating research plan...',
                10
            )

            plan = await self.lead_researcher.create_plan(query)

            # Enforce max_subagents limit
            if len(plan.tasks) > settings.max_subagents:
                logger.warning(f"Plan created {len(plan.tasks)} tasks, limiting to {settings.max_subagents}")
                plan.tasks = plan.tasks[:settings.max_subagents]

            self._send_progress(
                'planning_complete',
                f'Plan created: {len(plan.tasks)} research tasks identified',
                20,
                tasks=plan.tasks,
                rationale=plan.rationale
            )

            # Step 2: Execute subagents in parallel
            self._send_progress(
                'subagent_research',
                f'Spawning {len(plan.tasks)} research agents...',
                25
            )

            subagent_results = await self._execute_subagents_parallel(plan.tasks)

            self._send_progress(
                'subagent_complete',
                'All research agents completed',
                70
            )

            # Step 3: Synthesize findings
            self._send_progress(
                'synthesis',
                'Synthesizing findings into comprehensive report...',
                75
            )

            synthesis = await self.lead_researcher.synthesize(query, subagent_results)

            # Step 4: Add citations
            self._send_progress(
                'citation',
                'Adding citations and creating bibliography...',
                90
            )

            citation_result = await self.citation_agent.add_citations(
                synthesis,
                subagent_results
            )

            # Calculate metadata
            duration = time.time() - start_time
            metadata = {
                'subagents_count': len(plan.tasks),
                'sources_count': citation_result['source_count'],
                'duration_seconds': round(duration, 2)
            }

            # Create final result
            result = ResearchResult(
                query=query,
                plan=plan,
                subagent_results=subagent_results,
                synthesis=synthesis,
                cited_report=citation_result['cited_report'],
                bibliography=citation_result['bibliography'],
                metadata=metadata
            )

            self._send_progress(
                'complete',
                'Research complete!',
                100
            )

            logger.info(f"Research completed in {duration:.2f} seconds")

            return result

        except Exception as e:
            logger.error(f"Research failed: {e}", exc_info=True)
            self._send_progress(
                'error',
                f'Research failed: {str(e)}',
                0
            )
            raise

    async def _execute_subagents_parallel(self, tasks: List[str]) -> List[dict]:
        """
        Execute multiple subagents in parallel

        Args:
            tasks: List of research task strings

        Returns:
            List of subagent result dictionaries
        """
        logger.info(f"Executing {len(tasks)} subagents in parallel")

        # Create subagent instances
        subagents = [
            ResearchSubagent(
                llm=self.llm,
                tools=self.tools,
                task=task,
                agent_id=f"subagent_{i}"
            )
            for i, task in enumerate(tasks)
        ]

        # Execute all in parallel with progress tracking
        async def execute_with_progress(subagent, index):
            self._send_progress(
                'subagent_started',
                f'Starting research agent {index + 1}/{len(tasks)}',
                25 + (index * 45 // len(tasks)),
                subagent_id=subagent.agent_id,
                task=subagent.task
            )

            result = await subagent.research()

            self._send_progress(
                'subagent_finished',
                f'Completed research agent {index + 1}/{len(tasks)}',
                25 + ((index + 1) * 45 // len(tasks)),
                subagent_id=subagent.agent_id,
                findings_count=len(result['findings'].split('\n')),
                sources_count=len(result['sources'])
            )

            return result

        # Run all subagents concurrently
        results = await asyncio.gather(*[
            execute_with_progress(subagent, i)
            for i, subagent in enumerate(subagents)
        ], return_exceptions=True)

        # Filter out exceptions and log them
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Subagent {i} failed: {result}")
                # Create error result
                valid_results.append({
                    "agent_id": f"subagent_{i}",
                    "task": tasks[i],
                    "summary": f"Failed: {str(result)}",
                    "findings": f"Error: {str(result)}",
                    "sources": [],
                    "confidence": "low"
                })
            else:
                valid_results.append(result)

        return valid_results
