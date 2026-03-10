# CLAUDE.md - AgnostiChat Project Instructions

## Project Overview

AgnostiChat is a NiceGUI-based conversational interface that lets users query Elasticsearch using natural language. An LLM (OpenAI or Ollama) converts user questions into Elasticsearch DSL queries, executes them, and interprets the results.

## Architecture

```
User question
  → agnostichat/ui/app.py (NiceGUI page routing, event handlers)
    → agnostichat/ui/components.py (rendering functions)
    → agnostichat/ui/chat.py (chat business logic, question processing)
      → agnostichat/services/prompt_builder.py (builds prompt with mapping + samples)
      → agnostichat/services/llm_utils.py (sends to OpenAI or Ollama via LangChain)
      → LLM returns Elasticsearch DSL JSON
      → agnostichat/services/query_utils.py (adjusts .keyword fields)
      → agnostichat/services/elasticsearch_utils.py (executes query)
      → LLM interprets results
  → Display answer in chat
```

## Package Structure

```
agnostichat/                     # Main Python package
├── __init__.py                  # Package marker + __version__
├── __main__.py                  # Entry: python -m agnostichat
├── config.py                    # Centralized env config (Configuracao dataclass)
├── services/                    # Business logic layer
│   ├── __init__.py              # Re-exports all public functions
│   ├── elasticsearch_utils.py   # ES operations (connect, indices, mapping, queries)
│   ├── llm_utils.py            # LLM client factory (OpenAI / Ollama)
│   ├── prompt_builder.py        # Prompt engineering
│   └── query_utils.py          # Query post-processing (.keyword handling)
├── ui/                          # Presentation layer
│   ├── __init__.py
│   ├── app.py                   # Page routing, layout, ui.run(), event handlers
│   ├── styles.py               # CSS_PERSONALIZADO constant
│   ├── state.py                # EstadoApp class (uses config.py)
│   ├── components.py           # Rendering functions (landing, chat, sidebar, header)
│   └── chat.py                 # Chat business logic (processar_pergunta, extrair_json)
└── assets/                      # Static files
    └── logo_agnostichat.png
tests/                           # Test suite
├── __init__.py
├── conftest.py                  # Shared fixtures (mock ES, mock LLM)
└── test_services.py            # Tests for service modules
```

## Key Commands

```bash
# Run locally
python -m agnostichat

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

# Run tests
pytest
```

## Coding Conventions

- **Language**: Function names, variables, docstrings, and comments are in Portuguese. Documentation files (.md) are in English.
- **Style**: Follow ruff configuration in `pyproject.toml`. Line length 120. Double quotes.
- **Imports**: Standard library → third-party → local modules. Enforced by ruff isort. Use `agnostichat.` prefix for internal imports.
- **Type hints**: Add type hints to all new code. Existing code may lack them.
- **Error handling**: Prefer specific exception types over bare `except Exception`.
- **No global state**: Avoid module-level side effects. Use functions.
- **Separation of concerns**: Keep business logic in `services/`, UI rendering in `ui/components.py`, event handlers in `ui/app.py`.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `ES_HOST` | Elasticsearch URL | `http://localhost:9200` |
| `ES_API_KEY` | Elasticsearch API key | _(empty, optional)_ |
| `LLM_PROVIDER` | `"openai"` or `"ollama"` | `openai` |
| `LLM_API_KEY` | OpenAI API key | _(required for openai)_ |
| `PORT` | Application port | `8080` |
| `STORAGE_SECRET` | NiceGUI storage secret | `agnostichat-secret-key` |

## Dependencies

Managed via `requirements.txt`. Key packages:
- `nicegui` — UI framework (Vue/Quasar under the hood)
- `elasticsearch==8.12.1` — ES client (pinned)
- `langchain-openai`, `langchain-community` — LLM integration
- `python-dotenv` — env file loading
- `faker==22.6.0` — test data generation
- `pytest` — test framework

## Testing

- Use `pytest`
- Tests live in `tests/` directory
- Name files `test_*.py`
- Mock Elasticsearch and LLM clients
- Run with `pytest` or `pytest -v`

## Docker

- Main app: `docker-compose up` → port 8080
- ES test env: `docker-examples/elastic-test/docker-compose.yml`
- Ollama: `docker-examples/ollama/docker-compose.yml`
- Network: `agnostichat-network` (bridge) connects containers
