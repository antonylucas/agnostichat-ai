"""
Utilitários para interação com o LLM (OpenAI ou Ollama)
"""

from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI


def conectar_llm(api_key, provider="openai", ollama_host=None):
    """Retorna o cliente LLM configurado para OpenAI ou Ollama."""
    if provider == "openai":
        return ChatOpenAI(api_key=api_key, temperature=0.1)
    elif provider == "ollama (local)":
        # Sempre usa o nome do serviço Docker para Ollama
        return ChatOllama(base_url="http://ollama:11434", model="codellama:7b-instruct", temperature=0.1)
    else:
        raise ValueError("Provider LLM não suportado.")


def validar_llm(api_key: str, provider: str = "openai") -> bool:
    """Valida a conexão com o LLM enviando um prompt simples de teste."""
    client = conectar_llm(api_key, provider)
    resposta = client.invoke("Responda apenas: OK")
    conteudo = resposta.content if hasattr(resposta, "content") else str(resposta)
    if not conteudo or not conteudo.strip():
        raise ConnectionError("LLM retornou resposta vazia.")
    return True


def enviar_prompt_pergunta(llm_client, prompt, pergunta=None):
    """Envia o prompt ao LLM e retorna a resposta (query DSL)."""
    return llm_client.invoke(prompt)
