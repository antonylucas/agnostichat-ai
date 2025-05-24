"""
Função para estruturar o prompt enviado ao LLM
"""
import json

def describe_mapping(mapping, indent=0):
    """Gera uma descrição legível do mapping do Elasticsearch."""
    lines = []
    def _describe(props, prefix="", indent=0):
        for field, info in props.items():
            tipo = info.get("type", "object" if "properties" in info else "nested" if "nested" in info else "unknown")
            line = f"{'  '*indent}- {prefix}{field}: {tipo}"
            lines.append(line)
            if "properties" in info:
                _describe(info["properties"], prefix=prefix+field+".", indent=indent+1)
    props = mapping.get("properties", {})
    _describe(props, indent=indent)
    return "\n".join(lines)

def montar_prompt(nome_indice, mapping, tipos_dados, campos, amostras, pergunta):
    """Monta o prompt estruturado para o LLM com base no contexto do índice e pergunta do usuário."""
    describe = describe_mapping(mapping)
    amostras_str = "\n".join([json.dumps(a, ensure_ascii=False, indent=2) for a in amostras])
    prompt = f"""
Você é um assistente especializado em gerar queries DSL do Elasticsearch.
Utilize apenas as informações abaixo para responder à pergunta do usuário.

Nome do índice: {nome_indice}

Estrutura do índice (mapping):
{describe}

Exemplos de documentos:
{amostras_str}

Pergunta do usuário:
{pergunta}

IMPORTANTE:
- Retorne apenas o JSON da query DSL do Elasticsearch, sem GET, sem blocos de código, sem explicações ou comentários.
- Exemplo de resposta esperada: {{ "size": 0, "query": {{ ... }} }}
- Não inclua nenhum texto extra além do JSON.
"""
    return prompt 