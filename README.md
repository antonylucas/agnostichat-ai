# AgnostiChat

AgnostiChat é uma interface conversacional que permite usuários interagirem com dados armazenados no Elasticsearch usando linguagem natural. O sistema converte perguntas em queries DSL do Elasticsearch, tornando a busca e análise de dados mais acessível e intuitiva.

## Stack
- Python
- Streamlit (Frontend)
- Elasticsearch (Backend de dados)
- LLM (OpenAI API ou Ollama local)
- LangChain (integração com LLMs)
- python-dotenv (variáveis de ambiente)

## Funcionalidades
- Conexão fácil com Elasticsearch (host e API Key via interface ou .env)
- Seleção de índice e exibição do mapping e amostras reais
- Montagem automática de prompt detalhado para LLM
- Integração com OpenAI e Ollama (local)
- Geração automática de queries DSL do Elasticsearch via linguagem natural
- Execução da query e exibição dos resultados no chat
- Histórico de perguntas e respostas

## Como executar
```bash
# 1. Crie e ative um virtualenv (opcional, mas recomendado)
python3 -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows

# 2. Instale as dependências
pip install -r requirements.txt

# 3. (Opcional) Configure o arquivo .env na raiz do projeto
cp .env.example .env  # ou crie manualmente

# 4. Rode a aplicação
streamlit run app.py
```

## Exemplo de .env
```
ES_HOST=http://localhost:9200
ES_API_KEY=
LLM_API_KEY=
LLM_PROVIDER=openai
```

## Como usar
1. Preencha as credenciais na sidebar (ou use o .env para preencher automaticamente).
2. Clique em "Testar Conexão Elasticsearch".
3. Selecione um índice.
4. Veja o mapping e amostras de documentos.
5. Faça perguntas no chat usando linguagem natural.
6. Veja a query DSL gerada e os resultados.

## Dependências principais
- streamlit
- elasticsearch
- requests
- python-dotenv
- langchain-openai
- langchain-community

## Estrutura Inicial
- `app.py`: Aplicação principal
- `elasticsearch_utils.py`: Funções para interagir com o Elasticsearch
- `llm_utils.py`: Funções para interagir com o LLM
- `prompt_builder.py`: Montagem do prompt para o LLM
