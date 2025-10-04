# Multi-Agent Research System

A sophisticated research system powered by Claude Sonnet 4.5 and Parallel.ai that uses multiple AI agents working in parallel to conduct comprehensive research on any topic.

## Features

- **Multi-Agent Architecture**: Orchestrator-worker pattern with LeadResearcher coordinating specialized research agents
- **Parallel Research**: 3-5 agents research different aspects simultaneously
- **Automated Citations**: Comprehensive bibliography with inline citations
- **Web Search Integration**: Powered by Parallel.ai Search API
- **Progress Tracking**: Real-time updates on research progress
- **Multiple Output Formats**: Markdown, JSON, and HTML reports

## Architecture

```
User Query → LeadResearcher (Orchestrator)
                ↓
    ┌───────────┼───────────┐
    ↓           ↓           ↓
SubAgent1   SubAgent2   SubAgent3  (Parallel Workers)
    ↓           ↓           ↓
    └───────────┼───────────┘
                ↓
        Synthesis
                ↓
        CitationAgent
                ↓
        Final Report
```

### Agents

1. **LeadResearcher**: Analyzes queries, creates research plans, synthesizes findings
2. **ResearchSubagents**: Execute focused research tasks in parallel using web search
3. **CitationAgent**: Adds citations and creates bibliography

## Installation

### Prerequisites

- Python 3.10 or higher
- API keys:
  - Anthropic API key (for Claude Sonnet 4.5)
  - Parallel.ai API key (for web search)

### Setup

1. **Clone or navigate to the repository**:
   ```bash
   cd research-agent
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Virtual environment already created
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   PARALLEL_API_KEY=your_parallel_api_key_here
   ```

## Usage

### Command Line Interface

Run a research query from the command line:

```bash
python scripts/run_research.py "What are the environmental impacts of electric vehicles?"
```

The script will:
1. Display progress in real-time
2. Show research summary
3. Save results to `outputs/reports/` in Markdown, JSON, and HTML formats

### Python API

Use the research system programmatically:

```python
import asyncio
from research_system.core.orchestrator import MultiAgentResearchSystem

async def main():
    # Initialize system
    system = MultiAgentResearchSystem()

    # Run research
    result = await system.research(
        "What are the environmental impacts of electric vehicles?"
    )

    # Access results
    print(result.cited_report)
    print(f"Sources: {len(result.bibliography)}")

asyncio.run(main())
```

### With Progress Tracking

```python
from research_system.core.orchestrator import MultiAgentResearchSystem

def progress_callback(update):
    print(f"[{update.percent}%] {update.message}")

system = MultiAgentResearchSystem(progress_callback=progress_callback)
result = await system.research("Your query here")
```

## Project Structure

```
research-agent/
├── config/                      # Configuration and prompts
│   ├── settings.py             # Environment settings
│   └── prompts/                # Agent system prompts
│       ├── lead_researcher.py
│       ├── subagent.py
│       └── citation_agent.py
├── research_system/            # Main package
│   ├── core/                   # Core orchestration
│   │   ├── models.py          # Pydantic data models
│   │   └── orchestrator.py    # Multi-agent coordinator
│   ├── agents/                 # Agent implementations
│   │   ├── base.py
│   │   ├── lead_researcher.py
│   │   ├── subagent.py
│   │   └── citation_agent.py
│   ├── tools/                  # LangChain tools
│   │   └── parallel_search.py # Parallel.ai integration
│   └── utils/                  # Utilities
│       ├── parsers.py
│       ├── formatters.py
│       └── logging.py
├── scripts/                    # CLI scripts
│   └── run_research.py
├── examples/                   # Usage examples
│   └── simple_research.py
├── outputs/                    # Generated reports
│   └── reports/
└── logs/                       # Log files
```

## Configuration

Configure the system via `.env` file:

```bash
# API Keys (required)
ANTHROPIC_API_KEY=your_key_here
PARALLEL_API_KEY=your_key_here

# Model Configuration
MODEL_NAME=claude-sonnet-4-5-20250929
MODEL_TEMPERATURE=0.7
MAX_TOKENS=4096

# Research Configuration
MAX_SUBAGENTS=5
MIN_SUBAGENTS=3
PARALLEL_MAX_RESULTS=10
PARALLEL_MAX_CHARS=6000

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/research.log
```

## Output

Research results are saved in three formats:

### Markdown (`.md`)
Human-readable report with citations and bibliography

### JSON (`.json`)
Complete structured data including:
- Original query
- Research plan
- Subagent results
- Synthesis
- Citations
- Metadata

### HTML (`.html`)
Styled web page version of the report

## Examples

### Example 1: Environmental Research

```bash
python scripts/run_research.py "What are the environmental impacts of electric vehicles?"
```

Output includes:
- Carbon emissions analysis (manufacturing vs operation)
- Grid carbon intensity impact
- Battery lifecycle considerations
- Comprehensive citations

### Example 2: Technology Comparison

```bash
python scripts/run_research.py "Compare React vs Vue for enterprise applications"
```

The system will:
- Spawn agents to research React performance, Vue performance, and enterprise adoption
- Synthesize comparative analysis
- Provide cited recommendations

## How It Works

1. **Query Analysis**: LeadResearcher analyzes the query and identifies 3-5 research dimensions
2. **Task Decomposition**: Creates specific, non-overlapping research tasks
3. **Parallel Execution**: Spawns ResearchSubagents that work concurrently
4. **Web Research**: Each subagent uses Parallel.ai to search and gather information
5. **Synthesis**: LeadResearcher aggregates findings into coherent narrative
6. **Citation**: CitationAgent adds inline citations and bibliography
7. **Output**: Results saved in multiple formats

## Advanced Usage

### Custom Progress Tracking

```python
from rich.progress import Progress

with Progress() as progress:
    task = progress.add_task("Researching...", total=100)

    def callback(update):
        progress.update(task, completed=update.percent)

    system = MultiAgentResearchSystem(progress_callback=callback)
    result = await system.research(query)
```

### Batch Research

```python
queries = [
    "What is quantum computing?",
    "Explain blockchain technology",
    "What are the benefits of renewable energy?"
]

for query in queries:
    result = await system.research(query)
    print(f"Completed: {query}")
```

## Troubleshooting

### API Key Errors
Ensure your `.env` file has valid API keys:
```bash
# Check if .env exists
cat .env

# Verify keys are set
echo $ANTHROPIC_API_KEY
```

### Import Errors
Make sure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Parallel.ai Issues
If you don't have access to Parallel.ai yet:
1. Contact `support@parallel.ai` to request API access
2. See documentation at https://docs.parallel.ai

## Limitations

- Requires API keys for Claude and Parallel.ai
- Research quality depends on available web sources
- Processing time: 1-3 minutes for comprehensive research
- Token costs scale with research depth

## License

This project is for educational and research purposes.

## Credits

- **LLM**: Claude Sonnet 4.5 by Anthropic
- **Web Search**: Parallel.ai Search API
- **Framework**: LangChain

## Support

For issues or questions:
1. Check logs at `logs/research.log`
2. Review configuration in `.env`
3. Ensure API keys are valid

---

Built with ❤️ using Claude Sonnet 4.5, LangChain, and Parallel.ai
