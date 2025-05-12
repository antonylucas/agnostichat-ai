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

