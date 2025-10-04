from abc import ABC, abstractmethod
from langchain_anthropic import ChatAnthropic
from typing import Any, Dict


class BaseAgent(ABC):
    """Base class for all agents"""

    def __init__(self, llm: ChatAnthropic):
        """
        Initialize base agent

        Args:
            llm: ChatAnthropic language model instance
        """
        self.llm = llm

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Execute agent's primary function

        Returns:
            Dictionary with execution results
        """
        pass
