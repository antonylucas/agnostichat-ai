"""
Script para gerar dados de teste de customer analytics
"""

import random

from elasticsearch import Elasticsearch
from faker import Faker

# Configuração
INDEX_NAME = "customer_analytics"
NUM_DOCUMENTS = 1000

# Inicializa o Faker para gerar dados realistas
fake = Faker("pt_BR")

# Conecta ao Elasticsearch
es = Elasticsearch("http://agnostichat-elastic:9200")

# Mapping do índice
mapping = {
    "mappings": {
        "properties": {
            "customer_id": {"type": "keyword"},
            "name": {"type": "text"},
            "email": {"type": "keyword"},
            "age": {"type": "integer"},
            "gender": {"type": "keyword"},
            "city": {"type": "keyword"},
            "state": {"type": "keyword"},
            "registration_date": {"type": "date"},
            "last_purchase_date": {"type": "date"},
            "total_purchases": {"type": "integer"},
            "total_spent": {"type": "float"},
            "average_order_value": {"type": "float"},
            "preferred_category": {"type": "keyword"},
            "customer_segment": {"type": "keyword"},
            "satisfaction_score": {"type": "integer"},
            "is_active": {"type": "boolean"},
        }
    }
}


def generate_customer_data():
    """Gera um documento de customer analytics"""
    registration_date = fake.date_time_between(start_date="-2y", end_date="now")
    last_purchase = fake.date_time_between(start_date=registration_date, end_date="now")
    total_purchases = random.randint(1, 50)
    total_spent = round(random.uniform(100, 10000), 2)

    return {
        "customer_id": fake.uuid4(),
        "name": fake.name(),
        "email": fake.email(),
        "age": random.randint(18, 80),
        "gender": random.choice(["M", "F"]),
        "city": fake.city(),
        "state": fake.state_abbr(),
        "registration_date": registration_date.isoformat(),
        "last_purchase_date": last_purchase.isoformat(),
        "total_purchases": total_purchases,
        "total_spent": total_spent,
        "average_order_value": round(total_spent / total_purchases, 2),
        "preferred_category": random.choice(
            ["Eletrônicos", "Moda", "Casa", "Esportes", "Livros", "Alimentos", "Beleza", "Brinquedos"]
        ),
        "customer_segment": random.choice(["Bronze", "Prata", "Ouro", "Platina", "Diamante"]),
        "satisfaction_score": random.randint(1, 5),
        "is_active": random.choice([True, False]),
    }


def main():
    # Cria o índice se não existir
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Índice {INDEX_NAME} criado com sucesso!")

    # Gera e insere os documentos
    print(f"Gerando {NUM_DOCUMENTS} documentos...")
    for i in range(NUM_DOCUMENTS):
        doc = generate_customer_data()
        es.index(index=INDEX_NAME, body=doc)
        if (i + 1) % 100 == 0:
            print(f"Progresso: {i + 1}/{NUM_DOCUMENTS} documentos inseridos")

    # Força o refresh do índice
    es.indices.refresh(index=INDEX_NAME)

    # Conta os documentos
    count = es.count(index=INDEX_NAME)
    print(f"\nTotal de documentos no índice: {count['count']}")


if __name__ == "__main__":
    main()
