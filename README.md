# TrailGraph

AI agent running in a loop, powered by OpenRouter API, specialized in Salesforce sales and service processes.

## Requirements

- Python 3.12+
- OpenRouter API key

## Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

## Usage

**Interactive mode** (agent loop):
```bash
python main.py
```

**Single task mode**:
```bash
python main.py --task "Describe the lead qualification process"
```

**Verbose output**:
```bash
python main.py --verbose
```

## Project structure

```
TrailGraph/
├── agent/
│   ├── agent.py              # Agent loop
│   └── openrouter_client.py  # OpenRouter API client
├── tools/
│   └── base_tool.py          # Base class for all tools
├── prompts/
│   └── system.md             # System prompt
├── knowledge/
│   ├── sales/                # Salesforce sales process docs
│   └── service/              # Salesforce service process docs
├── main.py                   # Entry point, CLI
└── .env.example              # Environment variable template
```

## Adding a tool

Create a new file in `tools/` and extend `BaseTool`:

```python
from tools.base_tool import BaseTool

class MyTool(BaseTool):
    name = "my_tool"
    description = "What this tool does"

    def run(self, **kwargs):
        # tool logic here
        return "result"
```

## Adding knowledge

Add `.md` files to `knowledge/sales/` or `knowledge/service/` with domain documentation.
