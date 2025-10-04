# Quick Setup Guide

## Step 1: Activate Virtual Environment

```bash
source venv/bin/activate
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 3: Configure API Keys

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   # Open .env in your editor
   nano .env
   # or
   vim .env
   # or
   code .env
   ```

3. Add your keys:
   ```
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   PARALLEL_API_KEY=your-parallel-key-here
   ```

## Step 4: Test the Installation

Run the simple example:

```bash
python examples/simple_research.py
```

Or use the CLI:

```bash
python scripts/run_research.py "What is artificial intelligence?"
```

## Getting API Keys

### Anthropic API Key
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key

### Parallel.ai API Key
1. Visit https://platform.parallel.ai
2. Sign up for an account
3. Or contact support@parallel.ai to request access

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Make sure virtual environment is activated:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: Pydantic validation error on settings

**Solution**: Ensure .env file exists and has required keys:
```bash
cat .env
```

Should show:
```
ANTHROPIC_API_KEY=your_key
PARALLEL_API_KEY=your_key
```

### Issue: parallel-sdk not found

**Solution**: Install the Parallel SDK:
```bash
pip install parallel-sdk
```

If that fails, you may need to wait for API access from Parallel.ai.

## Directory Structure

```
research-agent/
├── venv/                       ✓ Virtual environment
├── .env                        ← Add your API keys here
├── README.md                   ← Full documentation
├── requirements.txt            ← Dependencies
├── config/                     ← Configuration
├── research_system/            ← Main package
├── scripts/                    ← CLI tools
├── examples/                   ← Usage examples
├── outputs/reports/            ← Generated reports
└── logs/                       ← Log files
```

## Next Steps

1. ✓ Virtual environment created
2. ✓ Dependencies installed
3. ✓ API keys configured
4. → Run your first research query!

Example query ideas:
- "What are the latest developments in quantum computing?"
- "Compare TypeScript vs JavaScript for large projects"
- "What are the health benefits of the Mediterranean diet?"
- "Explain how blockchain technology works"

Enjoy researching! 🚀
