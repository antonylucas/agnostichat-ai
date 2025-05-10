import streamlit as st
from elasticsearch_utils import conectar_elasticsearch, listar_indices, buscar_mapping, buscar_amostras
from prompt_builder import montar_prompt
from llm_utils import conectar_llm, enviar_prompt_pergunta
import json

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
    host = st.text_input("Host do Elasticsearch", value=st.session_state.get("es_host", ""))
    api_key = st.text_input("API Key do Elasticsearch", type="password", value=st.session_state.get("es_api_key", ""))

st.sidebar.header("🤖 Conexão LLM")
with st.sidebar.container():
    llm_provider = st.selectbox("Provider LLM", ["openai", "ollama"], index=0 if st.session_state.get("llm_provider") != "ollama" else 1)
    llm_api_key = st.text_input("API Key do LLM (OpenAI/Ollama)", type="password", value=st.session_state.get("llm_api_key", ""))

if st.sidebar.button("Testar Conexão Elasticsearch"):
    try:
        client = conectar_elasticsearch(host, api_key)
        indices = client.cat.indices()
        st.session_state["es_host"] = host
        st.session_state["es_api_key"] = api_key
        st.session_state["llm_api_key"] = llm_api_key
        st.session_state["llm_provider"] = llm_provider
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
                    st.code(query_dsl, language="json")
                    st.session_state["chat_history"].append({
                        "role": "assistant",
                        "content": "Query DSL sugerida:",
                        "query_dsl": query_dsl
                    })
                    with st.spinner("Executando query no Elasticsearch..."):
                        res = st.session_state["es_client"].search(
                            index=st.session_state["indice_selecionado"],
                            body=json.loads(query_dsl)
                        )
                        st.json(res["hits"]["hits"])
                        st.session_state["chat_history"].append({
                            "role": "assistant",
                            "content": "Resultados da consulta:",
                            "result": res["hits"]["hits"]
                        })
                except Exception as e:
                    st.error(f"Erro no processamento: {e}")
                    st.session_state["chat_history"].append({
                        "role": "assistant",
                        "content": f"Erro: {e}"
                    })
# ====== Exibição de Resultados ======
# (Já integrado ao chat) 