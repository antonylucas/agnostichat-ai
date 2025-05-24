import streamlit as st
from elasticsearch_utils import conectar_elasticsearch, listar_indices, buscar_mapping, buscar_amostras
from prompt_builder import montar_prompt
from llm_utils import conectar_llm, enviar_prompt_pergunta
import json
from dotenv import load_dotenv
import os
import re
from query_utils import ajustar_query_keyword

def salvar_configuracoes_env(host, api_key, llm_api_key, llm_provider):
    """Salva as configurações no arquivo .env"""
    env_content = f"""ES_HOST={host}
ES_API_KEY={api_key}
LLM_API_KEY={llm_api_key}
LLM_PROVIDER={llm_provider}
"""
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        return True
    except Exception as e:
        st.error(f"Erro ao salvar configurações: {e}")
        return False

def extrair_json(texto):
    # Primeiro tenta extrair bloco ```json ... ```
    match = re.search(r"```json\s*([\s\S]+?)\s*```", texto)
    if match:
        return match.group(1)
    # Se não encontrar, tenta extrair o primeiro bloco { ... }
    match = re.search(r"({[\s\S]+})", texto)
    if match:
        return match.group(1)
    # Se não encontrar, remove blocos de código simples e retorna
    return texto.strip('` \n')

load_dotenv()

# ====== Custom CSS para identidade visual ======
st.markdown(
    """
    <style>
    html, body, .main {
        background-color: #f5f6fa !important;
        font-family: 'Inter', 'Roboto', 'Segoe UI', Arial, sans-serif;
    }
    .stSidebar {
        background: #f2f4f8 !important;
        padding-top: 2em !important;
    }
    .sidebar-card {
        background: #fff;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        padding: 1em 1em 0.8em 1em;
        margin-bottom: 1em;
    }
    .sidebar-card h3 {
        font-size: 1.1em;
        font-weight: 600;
        margin-bottom: 0.7em;
        display: flex;
        align-items: center;
        gap: 0.5em;
    }
    .stButton>button {
        background: linear-gradient(90deg, #E60023 60%, #ff4b2b 100%);
        color: #fff;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1em;
        box-shadow: 0 2px 8px rgba(230,0,35,0.08);
        border: none;
        padding: 0.7em 0;
        width: 100%;
        margin-top: 1em;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background: #b8001a;
    }
    .stTextInput > div > div > input, .stTextInput input {
        padding: 0.6em 1em;
        border-radius: 8px;
        border: 1.5px solid #e0e0e0;
        font-size: 1em;
        background: #fafbfc;
        margin-bottom: 0.5em;
    }
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1.5px solid #e0e0e0 !important;
        font-size: 1em !important;
        background: #fafbfc !important;
    }
    .stSelectbox label, .stTextInput label {
        font-weight: 500;
        margin-bottom: 0.2em;
    }
    .st-bb {
        background: #fff;
        border-radius: 14px;
        padding: 1.2em 1em;
        margin-bottom: 1.2em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 0.5em 1em;
        margin-bottom: 0.5em;
        background: #f8fafd;
    }
    .stSidebar .css-1d391kg {
        font-size: 1.5em;
        color: #E60023;
        font-weight: bold;
    }
    .main-title {
        text-align: center;
        margin-top: 1.5em;
        margin-bottom: 0.2em;
        color: #E60023;
        font-size: 2.7em;
        font-weight: 800;
        letter-spacing: -1px;
    }
    .main-subtitle {
        text-align: center;
        color: #444;
        font-size: 1.1em;
        margin-bottom: 2em;
    }
    .status-card {
        background: #eaf3fb;
        color: #1a4b7a;
        border-radius: 10px;
        padding: 1em 1.5em;
        margin: 2em auto 0 auto;
        max-width: 600px;
        font-size: 1.1em;
        text-align: center;
        box-shadow: 0 2px 8px rgba(30,80,180,0.04);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ====== Sidebar com logo e inputs em cards ======
st.sidebar.image("assets/logo_agnostic.png", use_container_width=True)
st.sidebar.markdown("<h2 style='color:#E60023; margin-bottom:0;'>AgnostiChat</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<small>powered by AgnosticData</small>", unsafe_allow_html=True)

# Renderizar cards diretamente na sidebar, sem bloco with
st.sidebar.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
st.sidebar.markdown("<h3>🔗 Conexão Elasticsearch</h3>", unsafe_allow_html=True)
host = st.sidebar.text_input(
    "Host do Elasticsearch",
    value=st.session_state.get("es_host", os.getenv("ES_HOST", "")),
    placeholder="http://localhost:9200"
)
api_key = st.sidebar.text_input(
    "API Key do Elasticsearch",
    type="password",
    value=st.session_state.get("es_api_key", os.getenv("ES_API_KEY", "")),
    placeholder="Opcional"
)
st.sidebar.markdown("</div>", unsafe_allow_html=True)
st.sidebar.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
st.sidebar.markdown("<h3>🤖 Conexão LLM</h3>", unsafe_allow_html=True)
llm_provider_default = st.session_state.get("llm_provider", os.getenv("LLM_PROVIDER", "openai"))
llm_provider = st.sidebar.selectbox(
    "Provider LLM",
    ["openai", "ollama (local)"],
    index=0 if llm_provider_default != "ollama" else 1,
    key="llm_provider"
)

# Só mostra o campo de API Key se não for Ollama
if llm_provider != "ollama (local)":
    llm_api_key = st.sidebar.text_input(
        "API Key do LLM (OpenAI/Ollama)",
        type="password",
        value=st.session_state.get("llm_api_key", os.getenv("LLM_API_KEY", "")),
        placeholder="Cole sua chave aqui"
    )
else:
    llm_api_key = ""  # API Key vazia para Ollama
st.sidebar.markdown("</div>", unsafe_allow_html=True)
if st.sidebar.button("Testar Conexão"):
    try:
        client = conectar_elasticsearch(host, api_key)
        indices = client.cat.indices()
        # Salva as configurações no .env
        if salvar_configuracoes_env(host, api_key, llm_api_key, llm_provider):
            st.success("Configurações salvas com sucesso!")
        st.session_state["es_host"] = host
        st.session_state["es_api_key"] = api_key
        st.session_state["llm_api_key"] = llm_api_key
        st.session_state["es_client"] = client
        st.success("Conexão com Elasticsearch bem-sucedida! {0} índices encontrados.".format(len(indices.splitlines())))
    except Exception as e:
        st.session_state["es_client"] = None
        st.error(f"Erro ao conectar no Elasticsearch: {e}")

# ====== Título principal centralizado ======
st.markdown("<div class='main-title'>AgnostiChat</div>", unsafe_allow_html=True)
st.markdown("<div class='main-subtitle'>Interface conversacional para Elasticsearch com LLM</div>", unsafe_allow_html=True)

# ====== Seleção de Índice ======
if st.session_state.get("es_client"):
    with st.container():
        try:
            indices = listar_indices(st.session_state["es_client"])
            if indices:
                indice_selecionado = st.selectbox("Selecione um índice para consultar:", indices, key="indice_select")
                st.session_state["indice_selecionado"] = indice_selecionado
                st.info(f"Índice selecionado: {indice_selecionado}")

                # ====== Carregamento do Contexto do Índice ======
                if indice_selecionado:
                    if (st.session_state.get("mapping") is None or
                        st.session_state.get("mapping_indice") != indice_selecionado):
                        try:
                            mapping = buscar_mapping(st.session_state["es_client"], indice_selecionado)
                            amostras = buscar_amostras(st.session_state["es_client"], indice_selecionado, n=5)
                            st.session_state["mapping"] = mapping
                            st.session_state["amostras"] = amostras
                            st.session_state["mapping_indice"] = indice_selecionado
                        except Exception as e:
                            st.error(f"Erro ao buscar contexto do índice: {e}")
                            st.session_state["mapping"] = None
                            st.session_state["amostras"] = None
                    # Exibir contexto do índice
                    if st.session_state.get("mapping"):
                        st.markdown("<div class='st-bb'>", unsafe_allow_html=True)
                        st.subheader("Mapping do Índice")
                        st.json(st.session_state["mapping"])
                        st.markdown("</div>", unsafe_allow_html=True)
                    if st.session_state.get("amostras"):
                        st.markdown("<div class='st-bb'>", unsafe_allow_html=True)
                        st.subheader("Amostras de Documentos")
                        for i, doc in enumerate(st.session_state["amostras"], 1):
                            st.code(doc, language="json")
                        st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Nenhum índice encontrado no Elasticsearch.")
        except Exception as e:
            st.error(f"Erro ao listar índices: {e}")
else:
    st.markdown("<div class='status-card'>Conecte-se ao Elasticsearch para listar os índices.</div>", unsafe_allow_html=True)

# ====== Chat ======
if st.session_state.get("mapping") and st.session_state.get("amostras"):
    st.divider()
    st.subheader("💬 Chat com o Elasticsearch")
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("query_dsl"):
                st.code(msg["query_dsl"], language="json")
            if msg.get("result"):
                st.json(msg["result"])

    pergunta = st.chat_input("Digite sua pergunta sobre os dados deste índice...")
    if pergunta:
        with st.chat_message("user"):
            st.markdown(pergunta)
        st.session_state["chat_history"].append({"role": "user", "content": pergunta})
        with st.chat_message("assistant"):
            with st.spinner("Gerando query DSL com LLM..."):
                prompt = montar_prompt(
                    st.session_state["indice_selecionado"],
                    st.session_state["mapping"],
                    None,  # tipos_dados não usado
                    None,  # campos não usado
                    st.session_state["amostras"],
                    pergunta
                )
                try:
                    llm_client = conectar_llm(st.session_state["llm_api_key"], st.session_state["llm_provider"])
                    query_dsl = enviar_prompt_pergunta(llm_client, prompt, pergunta)
                    # Garante que query_dsl é uma string
                    if hasattr(query_dsl, "content"):
                        query_dsl_str = query_dsl.content
                    else:
                        query_dsl_str = str(query_dsl)
                    st.code(query_dsl_str, language="json")
                    st.session_state["chat_history"].append({
                        "role": "assistant",
                        "content": "Query DSL sugerida:",
                        "query_dsl": query_dsl_str
                    })
                    with st.spinner("Executando query no Elasticsearch..."):
                        query_dsl_json = extrair_json(query_dsl_str)
                        query_dict = json.loads(query_dsl_json)
                        # Ajuste automático de campos text para .keyword em agregações
                        query_dict = ajustar_query_keyword(query_dict, st.session_state["mapping"])
                        res = st.session_state["es_client"].search(
                            index=st.session_state["indice_selecionado"],
                            body=query_dict
                        )
                        # Exibe agregações se existirem, senão exibe hits
                        tem_aggs = "aggregations" in res
                        tem_hits = "hits" in res and res["hits"].get("hits")
                        if tem_aggs:
                            st.subheader("Resultado da agregação")
                            st.json(res["aggregations"])
                        if tem_hits:
                            st.json(res["hits"]["hits"])
                        # Monta prompt de interpretação considerando ambos
                        if tem_aggs and tem_hits:
                            prompt_interpretacao = f"""
Pergunta do usuário:
{pergunta}

Query DSL executada:
{query_dsl_json}

Resultado de agregação retornado do Elasticsearch:
{json.dumps(res['aggregations'], ensure_ascii=False, indent=2)}

Documentos retornados do Elasticsearch (mostrando até 10 exemplos):
{json.dumps(res['hits']['hits'][:10], ensure_ascii=False, indent=2)}

IMPORTANTE:
- Se a agregação não trouxer resultado, analise os documentos retornados e extraia a resposta a partir deles.
- Liste os valores únicos do campo mais relevante para a pergunta (ex: 'city' se a pergunta for sobre cidades).
- Responda de forma clara e objetiva, focando no que foi solicitado pelo usuário.
"""
                        elif tem_aggs:
                            prompt_interpretacao = f"""
Pergunta do usuário:
{pergunta}

Query DSL executada:
{query_dsl_json}

Resultado de agregação retornado do Elasticsearch:
{json.dumps(res['aggregations'], ensure_ascii=False, indent=2)}

Explique de forma resumida e clara o que significa esse resultado de agregação para o usuário.
"""
                        elif tem_hits:
                            exemplos = res["hits"]["hits"][:10] if isinstance(res["hits"]["hits"], list) else res["hits"]["hits"]
                            prompt_interpretacao = f"""
Pergunta do usuário:
{pergunta}

Query DSL executada:
{query_dsl_json}

Documentos retornados do Elasticsearch (mostrando até 10 exemplos):
{json.dumps(exemplos, ensure_ascii=False, indent=2)}

IMPORTANTE:
- Liste os valores únicos do campo mais relevante para a pergunta (ex: 'city' se a pergunta for sobre cidades).
- Responda de forma clara e objetiva, focando no que foi solicitado pelo usuário.
"""
                        else:
                            prompt_interpretacao = f"""
Pergunta do usuário:
{pergunta}

Query DSL executada:
{query_dsl_json}

Nenhum resultado retornado do Elasticsearch.
"""
                        st.session_state["chat_history"].append({
                            "role": "assistant",
                            "content": "Resultados da consulta:",
                            "result": res.get("aggregations", res["hits"]["hits"] if tem_hits else None)
                        })
                        # ====== Interpretação do resultado pelo LLM ======
                        interpretacao = enviar_prompt_pergunta(llm_client, prompt_interpretacao)
                        st.markdown("**Interpretação do resultado:**")
                        st.write(interpretacao.content if hasattr(interpretacao, 'content') else interpretacao)
                except Exception as e:
                    st.error(f"Erro no processamento: {e}")
                    st.session_state["chat_history"].append({
                        "role": "assistant",
                        "content": f"Erro: {e}"
                    })
# ====== Exibição de Resultados ======
# (Já integrado ao chat) 