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
    pass

def buscar_amostras(client, indice, n=3):
    """Retorna n amostras de documentos do índice."""
    pass 