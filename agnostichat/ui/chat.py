"""Lógica de negócio do chat — processamento de perguntas e interpretação de resultados."""

from __future__ import annotations

import json
import re

from agnostichat.services.llm_utils import conectar_llm, enviar_prompt_pergunta
from agnostichat.services.prompt_builder import montar_prompt
from agnostichat.services.query_utils import ajustar_query_keyword
from agnostichat.ui.state import EstadoApp


def extrair_json(texto: str) -> str:
    """Extrai JSON de uma string que pode conter blocos de código."""
    match = re.search(r"```json\s*([\s\S]+?)\s*```", texto)
    if match:
        return match.group(1)
    match = re.search(r"({[\s\S]+})", texto)
    if match:
        return match.group(1)
    return texto.strip("` \n")


def obter_sugestoes(indice: str | None) -> list[str]:
    """Retorna sugestões de perguntas com base no índice selecionado."""
    if not indice:
        return []
    return [
        f"Quantos documentos existem no índice {indice}?",
        f"Quais são os campos disponíveis em {indice}?",
        f"Mostre os 5 registros mais recentes de {indice}",
        f"Faça uma agregação dos dados de {indice}",
    ]


def montar_prompt_interpretacao(
    pergunta: str,
    query_dsl_json: str,
    resultado: dict,
    tem_aggs: bool,
    tem_hits: bool,
) -> str:
    """Monta o prompt de interpretação dos resultados do Elasticsearch."""
    if tem_aggs and tem_hits:
        return (
            f"Pergunta do usuário:\n{pergunta}\n\n"
            f"Query DSL executada:\n{query_dsl_json}\n\n"
            f"Resultado de agregação retornado do Elasticsearch:\n"
            f"{json.dumps(resultado['aggregations'], ensure_ascii=False, indent=2)}\n\n"
            f"Documentos retornados (até 10 exemplos):\n"
            f"{json.dumps(resultado['hits']['hits'][:10], ensure_ascii=False, indent=2)}\n\n"
            "IMPORTANTE:\n"
            "- Se a agregação não trouxer resultado, analise os documentos e extraia a resposta.\n"
            "- Liste os valores únicos do campo mais relevante para a pergunta.\n"
            "- Responda de forma clara e objetiva."
        )
    if tem_aggs:
        return (
            f"Pergunta do usuário:\n{pergunta}\n\n"
            f"Query DSL executada:\n{query_dsl_json}\n\n"
            f"Resultado de agregação retornado do Elasticsearch:\n"
            f"{json.dumps(resultado['aggregations'], ensure_ascii=False, indent=2)}\n\n"
            "Explique de forma resumida e clara o que significa esse resultado para o usuário."
        )
    if tem_hits:
        exemplos = resultado["hits"]["hits"][:10]
        return (
            f"Pergunta do usuário:\n{pergunta}\n\n"
            f"Query DSL executada:\n{query_dsl_json}\n\n"
            f"Documentos retornados (até 10 exemplos):\n"
            f"{json.dumps(exemplos, ensure_ascii=False, indent=2)}\n\n"
            "IMPORTANTE:\n"
            "- Liste os valores únicos do campo mais relevante para a pergunta.\n"
            "- Responda de forma clara e objetiva."
        )
    return (
        f"Pergunta do usuário:\n{pergunta}\n\n"
        f"Query DSL executada:\n{query_dsl_json}\n\n"
        "Nenhum resultado retornado do Elasticsearch."
    )


def processar_pergunta(estado: EstadoApp, texto: str) -> dict:
    """
    Processa uma pergunta do usuário: gera query DSL, executa no ES e interpreta o resultado.

    Args:
        estado: Estado da aplicação com conexões ativas.
        texto: Pergunta do usuário em linguagem natural.

    Returns:
        Dicionário com as chaves 'texto', 'query_dsl' e 'resultado'.

    Raises:
        json.JSONDecodeError: Se a resposta do LLM não contiver JSON válido.
        Exception: Se ocorrer erro na comunicação com ES ou LLM.
    """
    # Gera query DSL via LLM
    prompt = montar_prompt(
        estado.indice_selecionado,
        estado.mapping,
        None,
        None,
        estado.amostras,
        texto,
    )
    llm_client = conectar_llm(estado.llm_api_key, estado.llm_provider)
    resposta_llm = enviar_prompt_pergunta(llm_client, prompt, texto)
    query_dsl_str = resposta_llm.content if hasattr(resposta_llm, "content") else str(resposta_llm)

    # Extrai e ajusta a query
    query_dsl_json = extrair_json(query_dsl_str)
    query_dict = json.loads(query_dsl_json)
    query_dict = ajustar_query_keyword(query_dict, estado.mapping)

    # Executa no Elasticsearch
    resultado = estado.es_client.search(index=estado.indice_selecionado, body=query_dict)

    # Interpreta o resultado
    tem_aggs = "aggregations" in resultado
    tem_hits = "hits" in resultado and resultado["hits"].get("hits")

    prompt_interpretacao = montar_prompt_interpretacao(texto, query_dsl_json, resultado, tem_aggs, tem_hits)
    interpretacao = enviar_prompt_pergunta(llm_client, prompt_interpretacao)
    texto_interpretacao = interpretacao.content if hasattr(interpretacao, "content") else str(interpretacao)

    return {
        "texto": texto_interpretacao,
        "query_dsl": query_dsl_json,
        "resultado": resultado.get("aggregations") if tem_aggs else (resultado["hits"]["hits"] if tem_hits else None),
    }
