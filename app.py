import streamlit as st
from elasticsearch_utils import conectar_elasticsearch, listar_indices, buscar_mapping, buscar_amostras
from prompt_builder import montar_prompt
from llm_utils import conectar_llm, enviar_prompt_pergunta
import json
from dotenv import load_dotenv
import os
import re

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
    match = re.search(r"```json\s*([\s\S]+?)\s*```", texto)
    if match:
        return match.group(1)
    # Se não encontrar, tenta remover blocos de código simples
    return texto.strip('` \n')

load_dotenv()

# ====== Custom CSS para identidade visual ======
st.markdown(
    """
    <style>
    .main {
        background-color: #f7f7f7;
    }
    .stButton>button {
        background-color: #E60023;
        color: white;
        border-radius: 8px;
        font-weight: bold;
        transition: background 0.2s;
    }
    .stButton>button:hover {
        background-color: #b8001a;
    }
    .st-bb {
        background-color: #fff;
        border-radius: 10px;
        padding: 1em;
        margin-bottom: 1em;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }
    .stSidebar {
        background-color: #f2f4f8 !important;
    }
    .stTextInput > div > div > input, .stTextInput input {
        padding: 0.5em 1em;
        border-radius: 8px;
        border: 1.5px solid #eee;
        font-size: 1em;
        box-sizing: border-box;
    }
    .stSelectbox > div > div {
        border-radius: 8px !important;
        border: 1.5px solid #eee !important;
        font-size: 1em !important;
        /* padding: 0.5em 1em !important; */
        box-sizing: border-box;
    }
    .stSelectbox label, .stTextInput label {
        font-weight: 500;
        margin-bottom: 0.2em;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 0.5em 1em;
        margin-bottom: 0.5em;
    }
    .stSidebar .css-1d391kg { /* Título da sidebar */
        font-size: 1.5em;
        color: #E60023;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ====== Sidebar com logo e inputs ======
st.sidebar.image("assets/logo_agnostic.png", use_container_width=True)
st.sidebar.markdown("<h2 style='color:#E60023; margin-bottom:0;'>AgnostiChat</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<small>powered by AgnosticData</small>", unsafe_allow_html=True)

st.sidebar.header("🔗 Conexão Elasticsearch")
with st.sidebar.container():
    host = st.text_input(
        "Host do Elasticsearch",
        value=st.session_state.get("es_host", os.getenv("ES_HOST", ""))
    )
    api_key = st.text_input(
        "API Key do Elasticsearch",
        type="password",
        value=st.session_state.get("es_api_key", os.getenv("ES_API_KEY", ""))
    )

st.sidebar.header("🤖 Conexão LLM")
with st.sidebar.container():
    llm_provider_default = st.session_state.get("llm_provider", os.getenv("LLM_PROVIDER", "openai"))
    llm_provider = st.selectbox(
        "Provider LLM",
        ["openai", "ollama"],
        index=0 if llm_provider_default != "ollama" else 1,
        key="llm_provider"
    )
    llm_api_key = st.text_input(
        "API Key do LLM (OpenAI/Ollama)",
        type="password",
        value=st.session_state.get("llm_api_key", os.getenv("LLM_API_KEY", ""))
    )

if st.sidebar.button("Testar Conexão Elasticsearch"):
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

# ====== Título principal ======
st.markdown("""
<div style='display:flex; align-items:center; gap:1em;'>
</div>
""", unsafe_allow_html=True)
st.image("assets/logo_agnostic.png", width=60)
st.markdown("<h1 style='color:#E60023; margin-bottom:0; font-size:2.5em;'>AgnostiChat</h1>", unsafe_allow_html=True)
st.markdown("<small>Interface conversacional para Elasticsearch com LLM</small>", unsafe_allow_html=True)

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
    st.info("Conecte-se ao Elasticsearch para listar os índices.")

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
                        res = st.session_state["es_client"].search(
                            index=st.session_state["indice_selecionado"],
                            body=json.loads(query_dsl_json)
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

Documentos retornados do Elasticsearch (mostrando até 5 exemplos):
{json.dumps(res['hits']['hits'][:5], ensure_ascii=False, indent=2)}

Explique de forma resumida e clara o que significa esse resultado para o usuário, considerando tanto as agregações quanto os documentos.
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
                            exemplos = res["hits"]["hits"][:5] if isinstance(res["hits"]["hits"], list) else res["hits"]["hits"]
                            prompt_interpretacao = f"""
Pergunta do usuário:
{pergunta}

Query DSL executada:
{query_dsl_json}

Documentos retornados do Elasticsearch (mostrando até 5 exemplos):
{json.dumps(exemplos, ensure_ascii=False, indent=2)}

Resuma os principais achados ou padrões, ou responda à pergunta do usuário com base nesses documentos.
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