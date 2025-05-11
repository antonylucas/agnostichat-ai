# Configuração do Elasticsearch para AgnosticChat

Este diretório contém a configuração Docker para executar o Elasticsearch localmente para desenvolvimento e testes.

## Início Rápido

1. Certifique-se de ter o Docker e Docker Compose instalados
2. A partir deste diretório, execute:
   ```bash
   docker-compose up -d
   ```
3. O Elasticsearch estará disponível em http://localhost:9200

## Configuração

- A configuração usa Elasticsearch 8.12.1
- Recursos de segurança estão desativados para desenvolvimento
- Os dados são persistidos em um volume Docker
- Memória limitada a 512MB para uso em desenvolvimento

## Testando a Conexão

Você pode testar se o Elasticsearch está rodando fazendo uma requisição para:
```bash
curl http://localhost:9200
```

## Parando o Serviço

Para parar o Elasticsearch:
```bash
docker-compose down
```

Para parar e remover todos os dados:
```bash
docker-compose down -v
```
```

Agora vou criar uma versão de desenvolvimento do `elasticsearch_utils.py` que será mais adequada para testes locais:

```python:elasticsearch_utils_dev.py
"""
Utilitários para interação com o Elasticsearch (versão desenvolvimento)
"""

from elasticsearch import Elasticsearch

def conectar_elasticsearch(host="http://localhost:9200"):
    """Conecta ao Elasticsearch e retorna o client."""
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
```

Agora que temos todos os arquivos necessários, você pode:

1. Iniciar o Elasticsearch:
```bash
cd docker
docker-compose up -d
```

2. Aguardar alguns segundos para o Elasticsearch iniciar completamente

3. Testar a conexão usando o `elasticsearch_utils_dev.py`:
```python
from elasticsearch_utils_dev import conectar_elasticsearch, criar_indice, adicionar_documento

# Conectar ao Elasticsearch
client = conectar_elasticsearch()

# Criar um índice de teste
criar_indice(client, "teste")

# Adicionar um documento de teste
documento_teste = {
    "titulo": "Documento de Teste",
    "conteudo": "Este é um documento de teste para o AgnosticChat",
    "data": "2024-03-20"
}
adicionar_documento(client, "teste", documento_teste)
```

Gostaria que eu te ajudasse a criar um índice de teste com alguns dados para validarmos a configuração? 