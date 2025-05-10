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
Você é um assistente que gera queries DSL do Elasticsearch.\nUse apenas a estrutura do índice abaixo para responder à pergunta do usuário.\nInclua apenas a query DSL no seu output, sem explicações.\n\nNome do índice: {nome_indice}\n\nEstrutura do índice (mapping):\n{describe}\n\nExemplos de documentos:\n{amostras_str}\n\nPergunta do usuário:\n{pergunta}\n"""
    return prompt 