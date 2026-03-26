# TrailGraph — Claude Context

> **Always read `CLAUDE_PRIV.md` at the start of every conversation** — it contains user preferences and sensitive context not stored here.

## Project overview
AI agent running in a loop, powered by OpenRouter API, specialized in Salesforce sales and service processes.

## Stack
- Python 3.12+
- `httpx` — HTTP client for OpenRouter API
- `python-dotenv` — environment variable management

## Structure
- `agent/` — agent loop and OpenRouter client
- `tools/` — model tools, each extending `BaseTool`
- `prompts/` — system and task prompts as `.md` files
- `knowledge/` — domain knowledge (Salesforce processes) as `.md` files

## Language policy
- All documentation, comments, code identifiers, prompts, and any text not directly representing user data (e.g. file names, paths) must be written in **English**

## Commit message policy
- Use the `type: short description` format
- Allowed types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`
- Body (optional) explains the *why*, not the *what*
- No co-author lines, no AI attribution

### Branching & merging
- Changes to `agent/`, `tools/`, and `main.py` go through **pull requests** — no direct pushes to `main`
- Documentation and config files (`CLAUDE.md`, `requirements.txt`, `.gitignore`, etc.) may be pushed directly to `main`
- PRs are merged using **squash merge**
- The squash commit uses the dominant type of the PR with a summary title
- The body lists the individual commits that made up the PR:

```
feat: tool execution and agent loop improvements

- feat: add tool dispatcher to agent loop
- feat: implement search_knowledge tool for querying knowledge base
- fix: handle missing system prompt file gracefully
- fix: prevent empty user input from being sent to model
```

- Branch names should be short and descriptive (e.g. `threshold-experiment`, `pdf-support`)

### Pull request description format
PR title follows the same `type: short description` convention as commits.
PR body lists the individual commits that made up the branch:

```
feat: add Salesforce knowledge base and tool support

- feat: add lead_process and opportunity_stages knowledge files
- feat: add search_knowledge tool for querying .md files
- feat: load knowledge context into system prompt on startup
- refactor: split agent loop into step and loop methods
- fix: strip extra whitespace from loaded prompt files
```

## Key conventions
- Tools must extend `BaseTool` and implement `run()` and `parameters()`
- System prompt is loaded from `prompts/system.md` at agent startup
- Model is configured via `OPENROUTER_MODEL` env variable
- All secrets go in `.env`, never committed
