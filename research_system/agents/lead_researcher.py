from langchain.prompts import ChatPromptTemplate
from .base import BaseAgent
from research_system.core.models import ResearchPlan
from research_system.utils.parsers import parse_research_plan
from config.prompts.lead_researcher import (
    PLANNING_SYSTEM_PROMPT,
    SYNTHESIS_SYSTEM_PROMPT
)
from config.settings import settings
from research_system.utils.logging import get_logger
from typing import List

logger = get_logger(__name__)


class LeadResearcher(BaseAgent):
    """LeadResearcher agent - orchestrates research plan and synthesis"""

    def __init__(self, llm):
        """
        Initialize LeadResearcher

        Args:
            llm: ChatAnthropic language model instance
        """
        super().__init__(llm)
        self.planning_prompt = ChatPromptTemplate.from_messages([
            ("system", PLANNING_SYSTEM_PROMPT.format(
                min_subagents=settings.min_subagents,
                max_subagents=settings.max_subagents
            )),
            ("user", "Research query: {query}\n\nCreate a research plan.")
        ])
        self.synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", SYNTHESIS_SYSTEM_PROMPT),
            ("user", "Original Query: {query}\n\nSubagent Findings:\n{findings}\n\nSynthesize these findings into a comprehensive research report.")
        ])

    async def execute(self, query: str) -> ResearchPlan:
        """
        Main execution - create research plan

        Args:
            query: Research query string

        Returns:
            ResearchPlan object
        """
        return await self.create_plan(query)

    async def create_plan(self, query: str) -> ResearchPlan:
        """
        Analyze query and create research plan

        Args:
            query: Research query string

        Returns:
            ResearchPlan with tasks and rationale
        """
        logger.info(f"Creating research plan for query: {query[:100]}...")

        # Invoke LLM with planning prompt
        chain = self.planning_prompt | self.llm
        response = await chain.ainvoke({"query": query})

        # Parse XML output
        content = response.content
        parsed = parse_research_plan(content)

        logger.info(f"Created plan with {len(parsed['tasks'])} tasks")

        return ResearchPlan(
            tasks=parsed['tasks'],
            rationale=parsed['rationale']
        )

    async def synthesize(self, query: str, subagent_results: List[dict]) -> str:
        """
        Synthesize findings from all subagents

        Args:
            query: Original research query
            subagent_results: List of subagent result dictionaries

        Returns:
            Synthesized report as string
        """
        logger.info(f"Synthesizing findings from {len(subagent_results)} subagents")

        # Format findings for synthesis
        findings_text = self._format_findings(subagent_results)

        # Invoke synthesis
        chain = self.synthesis_prompt | self.llm
        response = await chain.ainvoke({
            "query": query,
            "findings": findings_text
        })

        logger.info("Synthesis complete")

        return response.content

    def _format_findings(self, subagent_results: List[dict]) -> str:
        """
        Format subagent findings for synthesis

        Args:
            subagent_results: List of subagent result dictionaries

        Returns:
            Formatted findings string
        """
        findings_text = ""

        for i, result in enumerate(subagent_results, 1):
            findings_text += f"\n\n{'='*80}\n"
            findings_text += f"SUBAGENT {i}: {result['task']}\n"
            findings_text += f"{'='*80}\n\n"

            findings_text += f"Summary:\n{result.get('summary', 'N/A')}\n\n"

            findings_text += f"Detailed Findings:\n{result.get('findings', 'N/A')}\n\n"

            sources = result.get('sources', [])
            if sources:
                findings_text += f"Sources Consulted ({len(sources)}):\n"
                for source in sources[:10]:  # Limit to first 10
                    findings_text += f"  - {source}\n"
                if len(sources) > 10:
                    findings_text += f"  ... and {len(sources) - 10} more\n"

            findings_text += f"\nConfidence: {result.get('confidence', 'N/A')}\n"

        return findings_text
