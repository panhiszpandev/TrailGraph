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

## Known issues

- **`pending_hint` leaks between steps** — after a successful answer, `pending_hint()` still returns the last visited node as a suggestion. It should only trigger after a fallback, not after every step. This causes the next unrelated question to receive a misleading hint.

## Planned improvements

### Near-term fixes
- **Fix `pending_hint` scope** — introduce a `has_pending` flag set only when `should_fallback()` triggers, so hints are only injected after an actual fallback.
- **Multi-path exploration** — explore top N candidate nodes in parallel (beam search), not just the single highest-scoring one.
- **Parser field names as constants** — field names in `graph/parser.py` (`summary:`, `parent:`, `children:`, etc.) are hardcoded strings; move to `config.py`.
- **Scoring module** — extract scoring logic and thresholds from `GetKnowledgeContext` into a dedicated `scoring.py` module, making scoring strategies easier to swap or extend.

### Longer-term

- **Document parser** — a tool that converts external documents (PDF, DOCX, Confluence pages, etc.) into the `.md` node format used by the knowledge graph, making it easier to populate and extend the knowledge base.

- **SQLite metadata store** — each knowledge node gets a corresponding record in a SQLite database holding only its metadata (`summary`, `parent`, `children`, `related`, `key_points`). Full content stays in the `.md` files and is loaded only when `view=focused`. Graph traversal and candidate selection happen against the database, making navigation faster without loading file contents on every hop.

- **RAG-based entry point selection** — replace the current fixed list of entry points with a RAG step. When a question arrives, RAG performs a semantic search across the knowledge graph and returns the top N most relevant nodes (default: 3) as candidate entry points. The existing graph traversal algorithm then runs from each candidate. If no confident match is found (score below threshold), the agent automatically falls back to the next RAG candidate (i+1) and retries — eliminating the need to hardcode entry points.

- **Multi-query decomposition** — if a user question can be split into N logical sub-questions, each sub-question is treated independently and goes through the full graph traversal algorithm on its own. The individual answers are then consolidated into a single response, evaluated for relevance against the original question.
