import re
from typing import List, Dict, Any
from research_system.core.models import Citation


def parse_research_plan(content: str) -> Dict[str, Any]:
    """
    Parse research plan XML from LLM output

    Args:
        content: LLM response containing research plan in XML format

    Returns:
        Dictionary with 'tasks' and 'rationale'
    """
    tasks = re.findall(r'<task>(.*?)</task>', content, re.DOTALL)
    rationale_match = re.search(r'<rationale>(.*?)</rationale>', content, re.DOTALL)

    return {
        'tasks': [task.strip() for task in tasks if task.strip()],
        'rationale': rationale_match.group(1).strip() if rationale_match else ""
    }


def extract_citations(text: str) -> List[str]:
    """
    Extract citation markers from text

    Args:
        text: Text containing citation markers

    Returns:
        List of unique citation markers found
    """
    citations = re.findall(r'\[Source \d+\]', text)
    return list(set(citations))


def parse_bibliography(text: str, sources: List[str]) -> List[Citation]:
    """
    Parse bibliography section into Citation objects

    Args:
        text: Text containing bibliography
        sources: List of source URLs from research

    Returns:
        List of Citation objects
    """
    citations = []

    # Look for bibliography section
    bib_match = re.search(
        r'(?:Bibliography|Sources|References):?\s*\n(.+)',
        text,
        re.DOTALL | re.IGNORECASE
    )

    if bib_match:
        bib_text = bib_match.group(1)

        # Parse individual citations
        citation_pattern = r'\[(\d+)\]\s*(.+?)(?:\n\[|$)'
        matches = re.finditer(citation_pattern, bib_text, re.DOTALL)

        for match in matches:
            index = int(match.group(1))
            citation_text = match.group(2).strip()

            # Extract URL
            url_match = re.search(r'URL:\s*(.+?)(?:\n|$)', citation_text)
            url = url_match.group(1).strip() if url_match else ""

            # Extract title (first line if no URL label)
            title_lines = citation_text.split('\n')
            title = title_lines[0].replace('URL:', '').strip()

            # Extract access date
            date_match = re.search(r'Accessed:\s*(.+?)(?:\n|$)', citation_text)
            accessed_date = date_match.group(1).strip() if date_match else ""

            citations.append(Citation(
                index=index,
                title=title if not title.startswith('http') else url,
                url=url if url else title,
                accessed_date=accessed_date
            ))

    else:
        # Fallback: create citations from source list
        from datetime import datetime
        current_date = datetime.now().strftime('%Y-%m-%d')

        for i, source_url in enumerate(sources, 1):
            citations.append(Citation(
                index=i,
                title=source_url,
                url=source_url,
                accessed_date=current_date
            ))

    return citations


def extract_summary(text) -> str:
    """
    Extract summary section from agent output

    Args:
        text: Agent output text (string or list)

    Returns:
        Extracted summary or first paragraph
    """
    # Handle list input (structured output)
    if isinstance(text, list):
        # If it's a list of dicts with 'text' key, extract and join
        if text and isinstance(text[0], dict):
            text = ' '.join(str(item.get('text', item)) for item in text)
        else:
            text = ' '.join(str(item) for item in text)

    # Convert to string if needed
    if not isinstance(text, str):
        text = str(text)

    # Look for summary section
    summary_match = re.search(
        r'##?\s*Summary:?\s*(.+?)(?:\n##|\n\n##|$)',
        text,
        re.DOTALL | re.IGNORECASE
    )

    if summary_match:
        return summary_match.group(1).strip()

    # Fallback: return first paragraph
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs[0] if paragraphs else text[:200]


def extract_sources_from_text(text) -> List[str]:
    """
    Extract URLs from text

    Args:
        text: Text potentially containing URLs (string or list)

    Returns:
        List of URLs found
    """
    # Handle case where text is already a list
    if isinstance(text, list):
        # If it's a list of dicts with 'url' key, extract URLs
        if text and isinstance(text[0], dict):
            return [item.get('url', '') for item in text if item.get('url')]
        # If it's a list of strings, join them
        text = ' '.join(str(item) for item in text)

    # Convert to string if needed
    if not isinstance(text, str):
        text = str(text)

    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return list(set(urls))  # Deduplicate
