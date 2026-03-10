"""Fixtures compartilhados para testes do AgnostiChat."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from agnostichat.config import Configuracao
from agnostichat.ui.state import EstadoApp


@pytest.fixture()
def config() -> Configuracao:
    """Retorna uma configuração de teste."""
    return Configuracao(
        es_host="http://localhost:9200",
        es_api_key="test-key",
        llm_api_key="test-llm-key",
        llm_provider="openai",
        porta=8080,
        storage_secret="test-secret",
    )


@pytest.fixture()
def estado(config: Configuracao) -> EstadoApp:
    """Retorna um EstadoApp com configuração de teste."""
    return EstadoApp(config=config)


@pytest.fixture()
def mock_es_client() -> MagicMock:
    """Retorna um mock do cliente Elasticsearch."""
    client = MagicMock()
    client.ping.return_value = True
    client.cat.indices.return_value = [
        {"index": "test-index-1"},
        {"index": "test-index-2"},
    ]
    client.indices.get_mapping.return_value = {
        "test-index-1": {
            "mappings": {
                "properties": {
                    "nome": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "idade": {"type": "integer"},
                }
            }
        }
    }
    client.search.return_value = {
        "hits": {
            "total": {"value": 1},
            "hits": [{"_source": {"nome": "Teste", "idade": 30}}],
        }
    }
    return client


@pytest.fixture()
def mock_llm_client() -> MagicMock:
    """Retorna um mock do cliente LLM."""
    client = MagicMock()
    response = MagicMock()
    response.content = '{"size": 10, "query": {"match_all": {}}}'
    client.invoke.return_value = response
    return client
