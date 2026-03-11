"""Configuração centralizada da aplicação via variáveis de ambiente."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Configuracao:
    """Valores de configuração carregados do ambiente (.env ou variáveis de sistema)."""

    es_host: str = field(default_factory=lambda: os.getenv("ES_HOST", ""))
    es_api_key: str = field(default_factory=lambda: os.getenv("ES_API_KEY", ""))
    es_user: str = field(default_factory=lambda: os.getenv("ES_USER", ""))
    es_password: str = field(default_factory=lambda: os.getenv("ES_PASSWORD", ""))
    llm_api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))
    llm_provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "openai"))
    porta: int = field(default_factory=lambda: int(os.getenv("PORT", "8080")))
    storage_secret: str = field(default_factory=lambda: os.getenv("STORAGE_SECRET", "agnostichat-secret-key"))
