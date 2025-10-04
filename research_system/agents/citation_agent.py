from langchain.prompts import ChatPromptTemplate
from .base import BaseAgent
from config.prompts.citation_agent import CITATION_SYSTEM_PROMPT
from research_system.utils.parsers import parse_bibliography
from research_system.utils.logging import get_logger
from typing import List, Dict
from datetime import datetime

logger = get_logger(__name__)


class CitationAgent(BaseAgent):
    """CitationAgent - ensures research integrity through proper citations"""

    def __init__(self, llm):
        """
        Initialize CitationAgent

        Args:
            llm: ChatAnthropic language model instance
        """
        super().__init__(llm)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", CITATION_SYSTEM_PROMPT),
            ("user", """Document to cite:
{document}

Available Sources:
{sources}

Add citations to all factual claims and create a bibliography.""")
        ])

    async def execute(self, document: str, subagent_results: List[dict]) -> Dict:
        """
        Main execution - add citations

        Args:
            document: Research report to cite
            subagent_results: List of subagent result dictionaries

        Returns:
            Dictionary with cited_report and bibliography
        """
        return await self.add_citations(document, subagent_results)

    async def add_citations(self, document: str, subagent_results: List[dict]) -> Dict:
        """
        Add citations to document based on sources from subagents

        Args:
            document: Research report text
            subagent_results: List of subagent result dictionaries

        Returns:
            Dictionary with 'cited_report', 'bibliography', 'source_count'
        """
        logger.info("Adding citations to research report")

        # Compile all sources
        all_sources, source_map = self._compile_sources(subagent_results)

        # Format sources for prompt
        sources_text = self._format_sources_for_prompt(all_sources, source_map)

        logger.info(f"Found {len(all_sources)} total sources to work with")

        # Invoke citation agent
        chain = self.prompt | self.llm
        response = await chain.ainvoke({
            "document": document,
            "sources": sources_text
        })

        cited_document = response.content

        # Parse bibliography from response
        bibliography = parse_bibliography(cited_document, all_sources)

        logger.info(f"Citations added. Bibliography has {len(bibliography)} entries")

        return {
            "cited_report": cited_document,
            "bibliography": bibliography,
            "source_count": len(all_sources)
        }

    def _compile_sources(self, subagent_results: List[dict]) -> tuple:
        """
        Compile all unique sources from subagent results

        Args:
            subagent_results: List of subagent result dictionaries

        Returns:
            Tuple of (all_sources list, source_map dict)
        """
        all_sources = []
        source_map = {}  # URL -> metadata

        for result in subagent_results:
            sources = result.get('sources', [])
            for url in sources:
                if url and url not in source_map:
                    all_sources.append(url)
                    source_map[url] = {
                        'url': url,
                        'task': result.get('task', 'Unknown'),
                        'agent_id': result.get('agent_id', 'Unknown')
                    }

        return all_sources, source_map

    def _format_sources_for_prompt(
        self,
        sources: List[str],
        source_map: Dict
    ) -> str:
        """
        Format sources for LLM prompt

        Args:
            sources: List of source URLs
            source_map: Dictionary mapping URLs to metadata

        Returns:
            Formatted string of sources
        """
        sources_text = ""
        current_date = datetime.now().strftime('%Y-%m-%d')

        for i, url in enumerate(sources, 1):
            sources_text += f"\n[Source {i}] {url}"
            meta = source_map.get(url, {})
            sources_text += f"\n  Related to: {meta.get('task', 'General research')}"
            sources_text += f"\n  Accessed: {current_date}"
            sources_text += "\n"

        return sources_text
