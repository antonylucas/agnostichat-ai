# AgnostiChat

AgnostiChat é uma interface conversacional que permite usuários interagirem com dados armazenados no Elasticsearch usando linguagem natural. O sistema converte perguntas em queries DSL do Elasticsearch, tornando a busca e análise de dados mais acessível e intuitiva.

## Stack
- Python
- Streamlit (Frontend)
- Elasticsearch (Backend de dados)
- LLM (OpenAI API ou Ollama local)

## Como executar
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estrutura Inicial
- `app.py`: Aplicação principal
- `elasticsearch_utils.py`: Funções para interagir com o Elasticsearch
- `llm_utils.py`: Funções para interagir com o LLM
- `prompt_builder.py`: Montagem do prompt para o LLM
