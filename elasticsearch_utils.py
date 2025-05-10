"""
Utilitários para interação com o Elasticsearch
"""

from elasticsearch import Elasticsearch

def conectar_elasticsearch(host, api_key):
    """Conecta ao Elasticsearch e retorna o client."""
    client = Elasticsearch(hosts=[host], api_key=api_key, verify_certs=False)
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
    query = {
        "size": n,
        "query": {
            "function_score": {
                "query": {"match_all": {}},
                "random_score": {}
            }
        }
    }
    res = client.search(index=indice, body=query)
    return [hit["_source"] for hit in res["hits"]["hits"]] 