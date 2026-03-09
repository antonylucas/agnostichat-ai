"""
Script para gerar dados de teste de marketing analytics
"""

import random

from elasticsearch import Elasticsearch
from faker import Faker

# Configuração
INDEX_NAME = "marketing_analytics"
NUM_DOCUMENTS = 3500

# Inicializa o Faker para gerar dados realistas
fake = Faker("pt_BR")

# Conecta ao Elasticsearch
es = Elasticsearch("http://agnostichat-elastic:9200")

# Mapping do índice
mapping = {
    "mappings": {
        "properties": {
            "campaign_id": {"type": "keyword"},
            "campaign_name": {"type": "text"},
            "channel": {"type": "keyword"},
            "start_date": {"type": "date"},
            "end_date": {"type": "date"},
            "budget": {"type": "float"},
            "spent": {"type": "float"},
            "impressions": {"type": "integer"},
            "clicks": {"type": "integer"},
            "conversions": {"type": "integer"},
            "conversion_rate": {"type": "float"},
            "ctr": {"type": "float"},
            "cpc": {"type": "float"},
            "cpa": {"type": "float"},
            "roi": {"type": "float"},
            "status": {"type": "keyword"},
            "target_audience": {"type": "keyword"},
            "campaign_type": {"type": "keyword"},
            "platform": {"type": "keyword"},
            "region": {"type": "keyword"},
        }
    }
}


def generate_marketing_data():
    """Gera um documento de marketing analytics"""
    start_date = fake.date_time_between(start_date="-1y", end_date="now")
    end_date = fake.date_time_between(start_date=start_date, end_date="now")
    budget = round(random.uniform(1000, 50000), 2)
    spent = round(random.uniform(budget * 0.5, budget), 2)
    impressions = random.randint(1000, 100000)
    clicks = random.randint(100, impressions)
    conversions = random.randint(10, clicks)

    return {
        "campaign_id": fake.uuid4(),
        "campaign_name": f"Campanha {fake.word().capitalize()} {fake.word().capitalize()}",
        "channel": random.choice(["Email", "Social Media", "Search", "Display", "Video", "Affiliate", "Direct"]),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "budget": budget,
        "spent": spent,
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "conversion_rate": round(conversions / clicks * 100, 2) if clicks > 0 else 0,
        "ctr": round(clicks / impressions * 100, 2) if impressions > 0 else 0,
        "cpc": round(spent / clicks, 2) if clicks > 0 else 0,
        "cpa": round(spent / conversions, 2) if conversions > 0 else 0,
        "roi": round((conversions * 100 - spent) / spent * 100, 2) if spent > 0 else 0,
        "status": random.choice(["Ativo", "Pausado", "Finalizado", "Agendado", "Cancelado"]),
        "target_audience": random.choice(
            ["Jovens", "Adultos", "Idosos", "Famílias", "Profissionais", "Estudantes", "Empresários"]
        ),
        "campaign_type": random.choice(
            ["Awareness", "Consideração", "Conversão", "Retenção", "Reativação", "Branding"]
        ),
        "platform": random.choice(
            ["Facebook", "Instagram", "Google", "LinkedIn", "Twitter", "TikTok", "YouTube", "Email"]
        ),
        "region": random.choice(["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul", "Nacional"]),
    }


def main():
    # Cria o índice se não existir
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME, body=mapping)
        print(f"Índice {INDEX_NAME} criado com sucesso!")

    # Gera e insere os documentos
    print(f"Gerando {NUM_DOCUMENTS} documentos...")
    for i in range(NUM_DOCUMENTS):
        doc = generate_marketing_data()
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
