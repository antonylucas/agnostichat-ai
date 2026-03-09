# CLAUDE.md - AgnostiChat Project Instructions

## Project Overview

AgnostiChat is a NiceGUI-based conversational interface that lets users query Elasticsearch using natural language. An LLM (OpenAI or Ollama) converts user questions into Elasticsearch DSL queries, executes them, and interprets the results.

## Architecture

```
User question
  → app_nicegui.py (NiceGUI UI, chat loop, orchestration)
    → prompt_builder.py (builds prompt with index mapping + sample docs)
    → llm_utils.py (sends to OpenAI or Ollama via LangChain)
    → LLM returns Elasticsearch DSL JSON
    → query_utils.py (adjusts .keyword fields for aggregations)
    → elasticsearch_utils.py (executes query)
    → LLM interprets results
  → Display answer in chat
```

## File Structure

- `app_nicegui.py` — Main NiceGUI application (UI, session state, chat loop, orchestration)
- `elasticsearch_utils.py` — Elasticsearch client wrapper (connect, list indices, mappings, sample docs, queries)
- `llm_utils.py` — LLM client factory (OpenAI via langchain-openai, Ollama via langchain-community)
- `prompt_builder.py` — Prompt engineering (structured prompt with mapping description and sample documents)
- `query_utils.py` — Query post-processing (auto-appends `.keyword` to text fields in aggregations)
- `requirements.txt` — Python dependencies
- `Dockerfile` / `docker-compose.yml` — Container orchestration
- `docker-examples/elastic-test/` — Standalone Elasticsearch with sample data generators
- `docker-examples/ollama/` — Standalone Ollama LLM setup

## Key Commands

```bash
# Run locally
python app_nicegui.py

# Run with Docker
docker-compose up --build

# Start Elasticsearch test env with sample data
cd docker-examples/elastic-test && docker-compose up --build

# Lint
ruff check .

# Format
ruff format .

# Type check
mypy .
```

## Coding Conventions

- **Language**: Function names, variables, docstrings, and comments are in Portuguese. Documentation files (.md) are in English.
- **Style**: Follow ruff configuration in `pyproject.toml`. Line length 120. Double quotes.
- **Imports**: Standard library → third-party → local modules. Enforced by ruff isort.
- **Type hints**: Add type hints to all new code. Existing code may lack them.
- **Error handling**: Prefer specific exception types over bare `except Exception`.
- **No global state**: Avoid module-level side effects. Use functions.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ES_HOST` | Elasticsearch URL | `http://localhost:9200` |
| `ES_API_KEY` | Elasticsearch API key | _(empty, optional)_ |
| `LLM_PROVIDER` | `"openai"` or `"ollama"` | `openai` |
| `LLM_API_KEY` | OpenAI API key | _(required for openai)_ |

## Dependencies

Managed via `requirements.txt`. Key packages:
- `nicegui` — UI framework (Vue/Quasar under the hood)
- `elasticsearch==8.12.1` — ES client (pinned)
- `langchain-openai`, `langchain-community` — LLM integration
- `python-dotenv` — env file loading
- `faker==22.6.0` — test data generation

## Testing

No test suite exists yet. When adding tests:
- Use `pytest`
- Place tests in a `tests/` directory
- Name files `test_*.py`
- Mock Elasticsearch and LLM clients

## Docker

- Main app: `docker-compose up` → port 8080
- ES test env: `docker-examples/elastic-test/docker-compose.yml`
- Ollama: `docker-examples/ollama/docker-compose.yml`
- Network: `agnostichat-network` (bridge) connects containers
