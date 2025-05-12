#!/bin/bash

# Função para verificar se o Elasticsearch está pronto
wait_for_elasticsearch() {
    echo "Aguardando Elasticsearch estar pronto..."
    while ! curl -s http://agnostichat-elastic:9200 > /dev/null; do
        sleep 1
    done
    echo "Elasticsearch está pronto!"
}

# Instala as dependências necessárias
pip install -r /app/requirements.txt

# Aguarda o Elasticsearch estar pronto
wait_for_elasticsearch

# Executa os scripts de geração de dados
echo "Iniciando geração de dados de exemplo..."
python /app/generate_customer_data.py
python /app/generate_marketing_data.py

echo "Dados de exemplo gerados com sucesso!" 