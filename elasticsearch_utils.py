"""
Utilitários para interação com o Elasticsearch (versão desenvolvimento)
"""

from elasticsearch import Elasticsearch


def conectar_elasticsearch(host="http://localhost:9200", api_key=None):
    """
    Conecta ao Elasticsearch e retorna o client.

    Args:
        host (str): Endpoint do Elasticsearch. Padrão: http://localhost:9200
        api_key (str, optional): Chave API para autenticação. Necessária para Elastic Cloud.

    Returns:
        Elasticsearch: Cliente conectado ao Elasticsearch
    """
    # Cria o cliente com os parâmetros apropriados
    if api_key:
        client = Elasticsearch(hosts=[host], verify_certs=False, api_key=api_key)
    else:
        client = Elasticsearch(hosts=[host], verify_certs=False)

    # Testa conexão
    if not client.ping():
        raise Exception("Não foi possível conectar ao Elasticsearch.")
    return client


def listar_indices(client):
    """Retorna a lista de índices disponíveis."""
    indices_info = client.cat.indices(format="json")
    return [idx["index"] for idx in indices_info]


def buscar_mapping(client, indice):
    """Retorna o mapping do índice informado."""
    return client.indices.get_mapping(index=indice)[indice]["mappings"]


def buscar_amostras(client, indice, n=5):
    """Retorna n amostras aleatórias de documentos do índice."""
    query = {"size": n, "query": {"function_score": {"query": {"match_all": {}}, "random_score": {}}}}
    res = client.search(index=indice, body=query)
    return [hit["_source"] for hit in res["hits"]["hits"]]


def criar_indice(client, nome_indice, mapping=None):
    """Cria um novo índice com o mapping opcional."""
    if not client.indices.exists(index=nome_indice):
        if mapping:
            client.indices.create(index=nome_indice, body=mapping)
        else:
            client.indices.create(index=nome_indice)
        return True
    return False


def adicionar_documento(client, indice, documento):
    """Adiciona um documento ao índice."""
    return client.index(index=indice, body=documento)
