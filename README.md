# TrailGraph

AI agent running in a loop, powered by OpenRouter API, specialized in Salesforce sales and service processes.

The agent navigates a graph-based knowledge base to answer questions — exploring nodes step by step rather than searching all files at once.

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
# Edit .env and add your OPENROUTER_API_KEY and OPENROUTER_MODEL
```

## Usage

**Interactive mode** (agent loop):
```bash
python main.py
```

**Single task mode**:
```bash
python main.py --task "How does lead qualification work?"
```

**Verbose output** (shows graph traversal step by step):
```bash
python main.py --verbose --task "How does lead qualification work?"
```

## How it works

The agent uses a `get_knowledge_context` tool to navigate the knowledge base as a graph:

1. Selects an entry point based on the question (CRM, Security, Integrations)
2. Explores nodes using `view=exploration` — receives `key_points`, `children`, and `related`
3. Drills into the most relevant node using `view=focused` — receives full content
4. Builds the final answer from collected context

The LLM never sees the full graph — it only sees the local view of the current node.

## Project structure

```
TrailGraph/
├── agent/
│   ├── agent.py              # Agent loop with tool calling
│   └── openrouter_client.py  # OpenRouter API client
├── tools/
│   ├── base_tool.py          # Base class for all tools
│   └── knowledge_tool.py     # get_knowledge_context tool
├── prompts/
│   └── system.md             # System prompt with graph navigation instructions
├── knowledge/
│   ├── entry_points/         # Top-level entry nodes (CRM, Security, Integrations)
│   ├── sales/                # Salesforce sales process nodes
│   └── service/              # Salesforce service process nodes
├── main.py                   # Entry point, CLI
└── .env.example              # Environment variable template
```

## Knowledge base node format

Each `.md` file in `knowledge/` follows this structure:

```markdown
# Node Title

summary: One-line description used for navigation decisions.
parent: path/to/Parent.md
children: [path/to/Child1.md, path/to/Child2.md]
related: [path/to/Related.md]
key_points: ["Key fact 1", "Key fact 2", "Key fact 3"]

## Content

Full content of the node used when view=focused.
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

Add `.md` files to the appropriate `knowledge/` subdirectory following the node format above. Update `parent`, `children`, and `related` fields to connect the node to the graph.
