from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate
from .base import BaseAgent
from config.prompts.subagent import SUBAGENT_SYSTEM_PROMPT
from research_system.utils.parsers import extract_summary, extract_sources_from_text
from research_system.utils.logging import get_logger
from typing import List

logger = get_logger(__name__)


class ResearchSubagent(BaseAgent):
    """ResearchSubagent - worker agent for focused research tasks"""

    def __init__(self, llm, tools: List, task: str, agent_id: str):
        """
        Initialize ResearchSubagent

        Args:
            llm: ChatAnthropic language model instance
            tools: List of LangChain tools
            task: Specific research task
            agent_id: Unique identifier for this subagent
        """
        super().__init__(llm)
        self.tools = tools
        self.task = task
        self.agent_id = agent_id
        self.prompt = self._create_prompt()

        # Create agent
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        # Create executor
        self.executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=False,
            max_iterations=10,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )

    def _create_prompt(self):
        """
        Create prompt template for subagent

        Returns:
            ChatPromptTemplate
        """
        return ChatPromptTemplate.from_messages([
            ("system", SUBAGENT_SYSTEM_PROMPT.format(task=self.task)),
            ("user", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

    async def execute(self) -> dict:
        """
        Execute research task

        Returns:
            Dictionary with research findings
        """
        return await self.research()

    def _extract_text_from_output(self, output) -> str:
        """
        Extract text from agent output, handling both string and structured formats

        Args:
            output: Agent output (can be string or list of content blocks)

        Returns:
            Text as string
        """
        # If it's already a string, return as-is
        if isinstance(output, str):
            return output

        # If it's a list of content blocks (structured output)
        if isinstance(output, list):
            text_parts = []
            for block in output:
                if isinstance(block, dict) and 'text' in block:
                    text_parts.append(block['text'])
                else:
                    text_parts.append(str(block))
            return ' '.join(text_parts)

        # Fallback: convert to string
        return str(output)

    async def research(self) -> dict:
        """
        Execute research task and return structured findings

        Returns:
            Dictionary with agent_id, task, summary, findings, sources, confidence
        """
        logger.info(f"[{self.agent_id}] Starting research: {self.task[:80]}...")

        try:
            # Run the agent
            result = await self.executor.ainvoke({
                "input": f"Research this topic thoroughly: {self.task}\n\nProvide comprehensive findings following the output format specified in your instructions.",
                "task": self.task
            })

            # Extract text from output (handles both string and structured formats)
            output_text = self._extract_text_from_output(result["output"])

            # Extract sources from intermediate steps
            sources = self._extract_sources(result.get("intermediate_steps", []))

            # Also extract sources from the output text
            output_sources = extract_sources_from_text(output_text)
            sources.extend(output_sources)
            sources = list(set(sources))  # Deduplicate

            # Extract summary
            summary = extract_summary(output_text)

            logger.info(f"[{self.agent_id}] Research complete. Found {len(sources)} sources")

            return {
                "agent_id": self.agent_id,
                "task": self.task,
                "summary": summary,
                "findings": output_text,
                "sources": sources,
                "confidence": self._extract_confidence(output_text)
            }

        except Exception as e:
            logger.error(f"[{self.agent_id}] Research failed: {e}", exc_info=True)
            return {
                "agent_id": self.agent_id,
                "task": self.task,
                "summary": f"Research failed: {str(e)}",
                "findings": f"Error occurred during research: {str(e)}",
                "sources": [],
                "confidence": "low"
            }

    def _extract_sources(self, intermediate_steps) -> List[str]:
        """
        Extract URLs from search results in intermediate steps

        Args:
            intermediate_steps: List of (AgentAction, result) tuples

        Returns:
            List of source URLs
        """
        sources = []

        for step in intermediate_steps:
            if len(step) >= 2:
                action, result = step[0], step[1]

                # Check if this was a search action
                if hasattr(action, 'tool') and 'search' in action.tool.lower():
                    # Extract URLs from result
                    result_text = str(result)
                    urls = extract_sources_from_text(result_text)
                    sources.extend(urls)

        return list(set(sources))  # Deduplicate

    def _extract_confidence(self, output: str) -> str:
        """
        Extract confidence level from agent output

        Args:
            output: Agent output text

        Returns:
            Confidence level (high/medium/low)
        """
        import re

        # Look for confidence assessment section
        confidence_match = re.search(
            r'##?\s*Confidence.*?:\s*(high|medium|low)',
            output,
            re.IGNORECASE | re.DOTALL
        )

        if confidence_match:
            return confidence_match.group(1).lower()

        # Default to medium
        return "medium"
