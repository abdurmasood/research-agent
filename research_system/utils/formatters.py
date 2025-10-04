from research_system.core.models import ResearchResult
import json
from datetime import datetime
import os


def format_as_markdown(result: ResearchResult) -> str:
    """
    Format research result as Markdown

    Args:
        result: ResearchResult object

    Returns:
        Markdown formatted string
    """
    md = f"# Research Report: {result.query}\n\n"
    md += f"*Generated: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    md += f"*Subagents used: {result.metadata.get('subagents_count', 'N/A')} | "
    md += f"Sources consulted: {result.metadata.get('sources_count', 'N/A')}*\n\n"
    md += "---\n\n"
    md += result.cited_report
    md += "\n\n---\n\n"

    # Add bibliography if not already in report
    if "Bibliography" not in result.cited_report and "References" not in result.cited_report:
        md += "## Bibliography\n\n"
        for cite in result.bibliography:
            md += f"{cite.index}. {cite.title}\n"
            md += f"   URL: {cite.url}\n"
            if cite.accessed_date:
                md += f"   Accessed: {cite.accessed_date}\n"
            md += "\n"

    return md


def format_as_json(result: ResearchResult) -> str:
    """
    Format research result as JSON

    Args:
        result: ResearchResult object

    Returns:
        JSON formatted string
    """
    return result.model_dump_json(indent=2)


def format_as_html(result: ResearchResult) -> str:
    """
    Format research result as HTML

    Args:
        result: ResearchResult object

    Returns:
        HTML formatted string
    """
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Research Report: {result.query}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; }}
        .metadata {{ color: #666; font-style: italic; margin-bottom: 20px; }}
        .report {{ line-height: 1.6; }}
        .bibliography {{ margin-top: 30px; }}
        .citation {{ margin-bottom: 10px; }}
    </style>
</head>
<body>
    <h1>Research Report: {result.query}</h1>
    <div class="metadata">
        Generated: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}<br>
        Subagents: {result.metadata.get('subagents_count', 'N/A')} |
        Sources: {result.metadata.get('sources_count', 'N/A')}
    </div>
    <hr>
    <div class="report">
        {result.cited_report.replace('\n', '<br>')}
    </div>
    <hr>
    <div class="bibliography">
        <h2>Bibliography</h2>
"""

    for cite in result.bibliography:
        html += f"""        <div class="citation">
            [{cite.index}] <strong>{cite.title}</strong><br>
            <a href="{cite.url}">{cite.url}</a><br>
            Accessed: {cite.accessed_date}
        </div>
"""

    html += """    </div>
</body>
</html>"""

    return html


def save_result(result: ResearchResult, output_dir: str = "outputs/reports") -> tuple:
    """
    Save research result to files

    Args:
        result: ResearchResult object
        output_dir: Directory to save files

    Returns:
        Tuple of (markdown_path, json_path, html_path)
    """
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Clean query for filename
    query_slug = "".join(c if c.isalnum() else "_" for c in result.query[:50])

    # Save as markdown
    md_path = os.path.join(output_dir, f"research_{timestamp}_{query_slug}.md")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(format_as_markdown(result))

    # Save as JSON
    json_path = os.path.join(output_dir, f"research_{timestamp}_{query_slug}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(format_as_json(result))

    # Save as HTML
    html_path = os.path.join(output_dir, f"research_{timestamp}_{query_slug}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(format_as_html(result))

    return md_path, json_path, html_path
