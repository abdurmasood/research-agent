from langchain.tools import tool
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables at module level
load_dotenv()


def get_parallel_search_tool():
    """Get configured Parallel.ai search tool"""

    # Get API key at initialization time
    api_key = os.getenv("PARALLEL_API_KEY")
    if not api_key:
        raise ValueError("PARALLEL_API_KEY environment variable not set. Check your .env file.")

    @tool
    def parallel_search(objective: str) -> str:
        """
        Search the web using Parallel.ai for research objectives.

        Args:
            objective: Natural language research goal or question

        Returns:
            Formatted search results with URLs and content excerpts
        """
        try:
            from parallel import Parallel
        except ImportError:
            raise ImportError(
                "Parallel SDK not installed. Install with: pip install parallel-web"
            )

        client = Parallel(api_key=api_key)

        # Get settings for configuration
        try:
            from config.settings import settings
            max_results = settings.parallel_max_results
            max_chars = settings.parallel_max_chars
            processor = settings.parallel_processor
        except Exception:
            # Fallback to defaults
            max_results = 10
            max_chars = 6000
            processor = "base"

        # Execute search
        search_response = client.beta.search(
            objective=objective,
            processor=processor,
            max_results=max_results,
            max_chars_per_result=max_chars
        )

        # Format results for LLM consumption
        return format_search_results(search_response.results)

    return parallel_search


def format_search_results(results: List[Any]) -> str:
    """
    Format Parallel.ai search results for LLM consumption

    Args:
        results: List of search result objects or dictionaries

    Returns:
        Formatted string with search results
    """
    if not results:
        return "No search results found."

    formatted = "SEARCH RESULTS:\n\n"

    for i, result in enumerate(results, 1):
        formatted += f"Result {i}:\n"

        # Handle both dict and object formats
        if isinstance(result, dict):
            title = result.get('title', 'N/A')
            url = result.get('url', 'N/A')
            excerpt = result.get('excerpt', result.get('content', ''))
        else:
            # Handle object attributes
            title = getattr(result, 'title', 'N/A')
            url = getattr(result, 'url', 'N/A')
            excerpt = getattr(result, 'excerpt', getattr(result, 'content', ''))

        formatted += f"Title: {title}\n"
        formatted += f"URL: {url}\n"

        # Add excerpt if available
        if excerpt:
            # Truncate if too long
            if len(excerpt) > 1000:
                excerpt = excerpt[:1000] + "..."
            formatted += f"Excerpt: {excerpt}\n"

        formatted += "\n" + "-" * 80 + "\n\n"

    return formatted


def extract_sources_from_results(results: List[Any]) -> List[str]:
    """
    Extract URLs from Parallel.ai search results

    Args:
        results: List of search result objects or dictionaries

    Returns:
        List of URLs
    """
    urls = []
    for result in results:
        if isinstance(result, dict):
            url = result.get('url', '')
        else:
            url = getattr(result, 'url', '')
        if url:
            urls.append(url)
    return urls
