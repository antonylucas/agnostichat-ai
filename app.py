import streamlit as st
from elasticsearch_utils import conectar_elasticsearch

st.set_page_config(page_title="AgnostiChat", layout="wide")

# ====== Tela de Conexão ======
st.sidebar.header("🔗 Conexão Elasticsearch")

host = st.sidebar.text_input("Host do Elasticsearch", value=st.session_state.get("es_host", ""))
api_key = st.sidebar.text_input("API Key do Elasticsearch", type="password", value=st.session_state.get("es_api_key", ""))

st.sidebar.header("🤖 Conexão LLM")
llm_api_key = st.sidebar.text_input("API Key do LLM (OpenAI/Ollama)", type="password", value=st.session_state.get("llm_api_key", ""))
llm_provider = st.sidebar.selectbox("Provider LLM", ["openai", "ollama"], index=0 if st.session_state.get("llm_provider") != "ollama" else 1)

if st.sidebar.button("Testar Conexão Elasticsearch"):
    try:
        client = conectar_elasticsearch(host, api_key)
        # Testa conexão listando índices
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

# ====== Seleção de Índice ======
# Dropdown para seleção de índice

# ====== Chat ======
# Campo para pergunta e exibição do contexto

# ====== Exibição de Resultados ======
# Área para mostrar resultados formatados 