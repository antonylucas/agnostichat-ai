"""
Utilitários para interação com o LLM (OpenAI ou Ollama)
"""
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
import os

def conectar_llm(api_key, provider="openai", ollama_host=None):
    """Retorna o cliente LLM configurado para OpenAI ou Ollama."""
    if provider == "openai":
        return ChatOpenAI(api_key=api_key, temperature=0.1)
    elif provider == "ollama":
        base_url = ollama_host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        return ChatOllama(base_url=base_url, temperature=0.1)
    else:
        raise ValueError("Provider LLM não suportado.")

def enviar_prompt_pergunta(llm_client, prompt, pergunta=None):
    """Envia o prompt ao LLM e retorna a resposta (query DSL)."""
    return llm_client.invoke(prompt) 