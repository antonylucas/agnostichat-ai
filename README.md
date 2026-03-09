# AgnostiChat

AgnostiChat is a conversational interface that allows users to interact with data stored in Elasticsearch using natural language. The system converts questions into Elasticsearch DSL queries, making data search and analysis more accessible and intuitive.

## Tech Stack

- Python
- NiceGUI (Frontend — Vue/Quasar under the hood)
- Elasticsearch (Data backend)
- LLM (OpenAI API or local Ollama)
- LangChain (LLM integration)
- python-dotenv (Environment variables)

## Features

- Easy Elasticsearch connection (host and API Key via UI or .env)
- Index selection with mapping and real sample data display
- Automatic detailed prompt assembly for the LLM
- Integration with OpenAI and Ollama (local)
- Automatic Elasticsearch DSL query generation from natural language
- Query execution and result display in chat
- Question and answer history

## Running with Docker

```bash
# 1. Clone the repository
git clone https://github.com/antonylucas/agnostichat-ai.git
cd agnostichat-ai

# 2. Configure the .env file (optional)
cp .env.example .env  # or create manually

# 3. Start the Docker containers
docker-compose up -d

# 4. Access the application
# Open http://localhost:8080 in your browser
```

## Running with virtualenv

```bash
# 1. Create and activate a virtualenv
python3 -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure the .env file at the project root
cp .env.example .env  # or create manually

# 4. Run the application
python app_nicegui.py
```

## Environment Variables

```
ES_HOST=http://localhost:9200
ES_API_KEY=
LLM_API_KEY=
LLM_PROVIDER=openai
```

See `.env.example` for a complete template with descriptions.

## How to Use

1. Fill in the credentials in the sidebar (or use .env for auto-fill).
2. Click "Conectar" (Connect).
3. Select an index.
4. Ask questions in the chat using natural language.
5. See the generated DSL query and results.

## Project Structure

- `app_nicegui.py` — Main application (NiceGUI frontend)
- `elasticsearch_utils.py` — Elasticsearch interaction utilities
- `llm_utils.py` — LLM interaction utilities
- `prompt_builder.py` — Prompt assembly for the LLM
- `query_utils.py` — Query adjustment utilities (.keyword field handling)

## Sample Data Setup

### Deploying Elasticsearch and Generating Sample Indices

1. Navigate to the container directory:
```bash
cd docker-examples/elastic-test
```

2. Start Elasticsearch and generate sample data automatically:
```bash
docker-compose up --build
```

Elasticsearch will be available at `http://agnostichat-elastic:9200` within the Docker network.
The `customer_analytics` and `marketing_analytics` indices will be created automatically with sample data.

#### (Optional) Generate Data Manually

If you need to regenerate the data:
```bash
cd docker-examples/elastic-test/data-sample
python generate_customer_data.py
python generate_marketing_data.py
```

After running, you can use AgnostiChat to query this data using natural language.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## Development

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy .
```

See [CLAUDE.md](CLAUDE.md) for detailed project instructions and coding conventions.
