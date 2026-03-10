"""Estado global da aplicação (por sessão NiceGUI)."""

from __future__ import annotations

from typing import Any

from agnostichat.config import Configuracao


class EstadoApp:
    """Gerencia o estado global da aplicação."""

    def __init__(self, config: Configuracao | None = None) -> None:
        cfg = config or Configuracao()
        self.es_host: str = cfg.es_host
        self.es_api_key: str = cfg.es_api_key
        self.llm_api_key: str = cfg.llm_api_key
        self.llm_provider: str = cfg.llm_provider
        self.es_client: Any = None
        self.conectado: bool = False
        self.indices: list[str] = []
        self.indice_selecionado: str | None = None
        self.mapping: dict | None = None
        self.amostras: list | None = None
        self.mapping_indice: str | None = None
        self.mensagens_chat: list[dict] = []
        self.chat_iniciado: bool = False
