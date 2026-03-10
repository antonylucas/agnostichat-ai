"""Camada de serviços — lógica de negócio independente de UI."""

from agnostichat.services.elasticsearch_utils import (
    adicionar_documento,
    buscar_amostras,
    buscar_mapping,
    conectar_elasticsearch,
    criar_indice,
    listar_indices,
)
from agnostichat.services.llm_utils import conectar_llm, enviar_prompt_pergunta
from agnostichat.services.prompt_builder import describe_mapping, montar_prompt
from agnostichat.services.query_utils import ajustar_query_keyword, get_field_type, has_keyword_subfield

__all__ = [
    "adicionar_documento",
    "ajustar_query_keyword",
    "buscar_amostras",
    "buscar_mapping",
    "conectar_elasticsearch",
    "conectar_llm",
    "criar_indice",
    "describe_mapping",
    "enviar_prompt_pergunta",
    "get_field_type",
    "has_keyword_subfield",
    "listar_indices",
    "montar_prompt",
]
