"""
AgnostiChat — Interface conversacional para Elasticsearch com NiceGUI.

Frontend moderno estilo ChatGPT/Claude com sidebar lateral,
página de landing e chat interativo.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from nicegui import ui

from elasticsearch_utils import buscar_amostras, buscar_mapping, conectar_elasticsearch, listar_indices
from llm_utils import conectar_llm, enviar_prompt_pergunta
from prompt_builder import montar_prompt
from query_utils import ajustar_query_keyword

load_dotenv()

# ====== CSS customizado ======
CSS_PERSONALIZADO = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --cor-primaria: #E60023;
    --cor-fundo: #FAFAF8;
    --cor-sidebar: #F7F7F5;
    --cor-borda: #E8E8E5;
    --cor-texto: #2D2D2D;
    --cor-texto-secundario: #6B6B6B;
    --cor-mensagem-usuario: #F4F4F2;
    --cor-mensagem-assistente: #FFFFFF;
}

body, .q-page, .nicegui-content {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--cor-fundo) !important;
}

.q-drawer {
    background-color: var(--cor-sidebar) !important;
    border-right: 1px solid var(--cor-borda) !important;
}

.q-header {
    background-color: var(--cor-fundo) !important;
    border-bottom: 1px solid var(--cor-borda) !important;
}

.chat-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 1rem;
}

.mensagem-usuario {
    background-color: var(--cor-mensagem-usuario) !important;
    border-radius: 18px !important;
    padding: 12px 18px !important;
    max-width: 85%;
    margin-left: auto !important;
}

.mensagem-assistente {
    background-color: var(--cor-mensagem-assistente) !important;
    border-radius: 18px !important;
    padding: 12px 18px !important;
    max-width: 85%;
    border: 1px solid var(--cor-borda);
}

.chip-sugestao {
    border: 1.5px solid var(--cor-borda) !important;
    border-radius: 20px !important;
    background: white !important;
    color: var(--cor-texto) !important;
    font-size: 0.85rem !important;
    padding: 8px 16px !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

.chip-sugestao:hover {
    border-color: var(--cor-primaria) !important;
    background: #FFF5F5 !important;
}

.campo-entrada {
    max-width: 800px;
    margin: 0 auto;
}

.campo-entrada .q-field__control {
    border-radius: 24px !important;
    border: 1.5px solid var(--cor-borda) !important;
    padding: 4px 8px !important;
    background: white !important;
}

.campo-entrada .q-field__control:focus-within {
    border-color: var(--cor-primaria) !important;
    box-shadow: 0 0 0 2px rgba(230, 0, 35, 0.1) !important;
}

.botao-conectar {
    background: linear-gradient(135deg, #E60023 0%, #FF4B4B 100%) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

.cartao-config {
    background: white;
    border-radius: 12px;
    border: 1px solid var(--cor-borda);
    padding: 16px;
    margin-bottom: 12px;
}

.landing-titulo {
    font-size: 2.5rem;
    font-weight: 800;
    color: var(--cor-texto);
    letter-spacing: -1px;
    line-height: 1.2;
}

.landing-subtitulo {
    font-size: 1.1rem;
    color: var(--cor-texto-secundario);
    margin-top: 8px;
}

.bloco-codigo-query {
    background: #1E1E1E;
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
    overflow-x: auto;
}

.indicador-status {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
}

.status-conectado { background-color: #22C55E; }
.status-desconectado { background-color: #EF4444; }
"""


class EstadoApp:
    """Gerencia o estado global da aplicação."""

    def __init__(self) -> None:
        self.es_host: str = os.getenv("ES_HOST", "")
        self.es_api_key: str = os.getenv("ES_API_KEY", "")
        self.llm_api_key: str = os.getenv("LLM_API_KEY", "")
        self.llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
        self.es_client: Any = None
        self.conectado: bool = False
        self.indices: list[str] = []
        self.indice_selecionado: str | None = None
        self.mapping: dict | None = None
        self.amostras: list | None = None
        self.mapping_indice: str | None = None
        self.mensagens_chat: list[dict] = []
        self.chat_iniciado: bool = False


def extrair_json(texto: str) -> str:
    """Extrai JSON de uma string que pode conter blocos de código."""
    match = re.search(r"```json\s*([\s\S]+?)\s*```", texto)
    if match:
        return match.group(1)
    match = re.search(r"({[\s\S]+})", texto)
    if match:
        return match.group(1)
    return texto.strip("` \n")


def obter_sugestoes(indice: str | None) -> list[str]:
    """Retorna sugestões de perguntas com base no índice selecionado."""
    if not indice:
        return []
    return [
        f"Quantos documentos existem no índice {indice}?",
        f"Quais são os campos disponíveis em {indice}?",
        f"Mostre os 5 registros mais recentes de {indice}",
        f"Faça uma agregação dos dados de {indice}",
    ]


@ui.page("/")
def pagina_principal() -> None:
    """Página principal da aplicação."""
    estado = EstadoApp()

    # Referências para atualização dinâmica da UI
    refs: dict = {
        "area_chat": None,
        "container_chat": None,
        "container_principal": None,
        "entrada_texto": None,
        "label_status": None,
        "select_indice": None,
    }

    # ====== Funções de evento ======

    async def ao_conectar() -> None:
        """Tenta conectar ao Elasticsearch."""
        if not estado.es_host:
            ui.notify("Informe o host do Elasticsearch", type="warning")
            return
        try:
            estado.es_client = conectar_elasticsearch(estado.es_host, estado.es_api_key or None)
            estado.conectado = True
            estado.indices = listar_indices(estado.es_client)
            ui.notify(f"Conectado! {len(estado.indices)} índices encontrados.", type="positive")
            atualizar_interface()
        except Exception as e:
            estado.conectado = False
            estado.es_client = None
            ui.notify(f"Erro ao conectar: {e}", type="negative")

    def ao_selecionar_indice(valor: str | None) -> None:
        """Carrega mapping e amostras ao selecionar um índice."""
        if not valor or not estado.es_client:
            return
        estado.indice_selecionado = valor
        try:
            if estado.mapping_indice != valor:
                estado.mapping = buscar_mapping(estado.es_client, valor)
                estado.amostras = buscar_amostras(estado.es_client, valor, n=5)
                estado.mapping_indice = valor
            estado.chat_iniciado = True
            estado.mensagens_chat = []
            atualizar_interface()
        except Exception as e:
            ui.notify(f"Erro ao carregar índice: {e}", type="negative")

    async def ao_enviar_mensagem(pergunta: str | None = None) -> None:
        """Processa uma pergunta do usuário."""
        texto = pergunta or (refs["entrada_texto"].value if refs["entrada_texto"] else None)
        if not texto or not texto.strip():
            return
        if refs["entrada_texto"]:
            refs["entrada_texto"].value = ""

        # Adiciona mensagem do usuário
        estado.mensagens_chat.append({"papel": "usuario", "conteudo": texto})
        renderizar_mensagem("usuario", texto)

        # Indicador de carregamento
        with refs["container_chat"]:
            carregando = ui.row().classes("items-center gap-2 p-3")
            with carregando:
                ui.spinner("dots", size="sm", color="grey")
                ui.label("Gerando consulta...").classes("text-grey-6 text-sm")

        # Rola para baixo
        await ui.run_javascript("document.querySelector('.area-rolagem')?.scrollTo({top: 999999, behavior: 'smooth'})")

        try:
            # Gera query DSL via LLM
            prompt = montar_prompt(
                estado.indice_selecionado,
                estado.mapping,
                None,
                None,
                estado.amostras,
                texto,
            )
            llm_client = conectar_llm(estado.llm_api_key, estado.llm_provider)
            resposta_llm = enviar_prompt_pergunta(llm_client, prompt, texto)
            query_dsl_str = resposta_llm.content if hasattr(resposta_llm, "content") else str(resposta_llm)

            # Executa query no Elasticsearch
            carregando.clear()
            with carregando:
                ui.spinner("dots", size="sm", color="grey")
                ui.label("Executando consulta...").classes("text-grey-6 text-sm")

            query_dsl_json = extrair_json(query_dsl_str)
            query_dict = json.loads(query_dsl_json)
            query_dict = ajustar_query_keyword(query_dict, estado.mapping)

            resultado = estado.es_client.search(index=estado.indice_selecionado, body=query_dict)

            # Interpreta resultado
            tem_aggs = "aggregations" in resultado
            tem_hits = "hits" in resultado and resultado["hits"].get("hits")

            prompt_interpretacao = _montar_prompt_interpretacao(texto, query_dsl_json, resultado, tem_aggs, tem_hits)

            interpretacao = enviar_prompt_pergunta(llm_client, prompt_interpretacao)
            texto_interpretacao = interpretacao.content if hasattr(interpretacao, "content") else str(interpretacao)

            # Remove indicador de carregamento e mostra resposta
            carregando.delete()

            conteudo_resposta = {
                "texto": texto_interpretacao,
                "query_dsl": query_dsl_json,
                "resultado": resultado.get("aggregations")
                if tem_aggs
                else (resultado["hits"]["hits"] if tem_hits else None),
            }

            estado.mensagens_chat.append({"papel": "assistente", "conteudo": conteudo_resposta})
            renderizar_mensagem("assistente", conteudo_resposta)

        except json.JSONDecodeError:
            carregando.delete()
            msg_erro = "Não foi possível interpretar a query DSL gerada. Tente reformular sua pergunta."
            estado.mensagens_chat.append({"papel": "assistente", "conteudo": {"texto": msg_erro}})
            renderizar_mensagem("assistente", {"texto": msg_erro})

        except Exception as e:
            carregando.delete()
            msg_erro = f"Erro no processamento: {e}"
            estado.mensagens_chat.append({"papel": "assistente", "conteudo": {"texto": msg_erro}})
            renderizar_mensagem("assistente", {"texto": msg_erro})

        # Rola para baixo
        await ui.run_javascript("document.querySelector('.area-rolagem')?.scrollTo({top: 999999, behavior: 'smooth'})")

    def renderizar_mensagem(papel: str, conteudo: str | dict) -> None:
        """Renderiza uma mensagem no container do chat."""
        with refs["container_chat"]:
            if papel == "usuario":
                with ui.row().classes("w-full justify-end mb-3"):
                    ui.html(f'<div class="mensagem-usuario">{conteudo}</div>')
            else:
                with ui.column().classes("w-full mb-3"):
                    dados = conteudo if isinstance(conteudo, dict) else {"texto": conteudo}

                    with ui.element("div").classes("mensagem-assistente"):
                        # Texto da interpretação
                        if dados.get("texto"):
                            ui.markdown(dados["texto"]).classes("text-sm")

                        # Query DSL em bloco de código
                        if dados.get("query_dsl"):
                            with ui.expansion("Ver Query DSL", icon="code").classes("w-full mt-2"):
                                ui.code(dados["query_dsl"], language="json").classes("w-full")

                        # Resultado bruto
                        if dados.get("resultado"):
                            with ui.expansion("Ver resultado bruto", icon="data_object").classes("w-full mt-1"):
                                resultado_str = json.dumps(dados["resultado"], ensure_ascii=False, indent=2)
                                ui.code(resultado_str, language="json").classes("w-full")

    def atualizar_interface() -> None:
        """Reconstrói a área principal com base no estado atual."""
        refs["container_principal"].clear()
        with refs["container_principal"]:
            if not estado.conectado:
                renderizar_landing()
            elif not estado.chat_iniciado:
                renderizar_selecao_indice()
            else:
                renderizar_chat()

    def renderizar_landing() -> None:
        """Renderiza a página de landing (não conectado)."""
        with ui.column().classes("w-full items-center justify-center min-h-[70vh] gap-6"):
            ui.image("assets/logo_agnostic.png").classes("w-24 h-24 opacity-80")
            ui.html('<div class="landing-titulo">AgnostiChat</div>')
            ui.html('<div class="landing-subtitulo">Interface conversacional para Elasticsearch com IA</div>')
            with (
                ui.card()
                .classes("w-full max-w-md p-6 mt-4")
                .style("border-radius: 16px; border: 1px solid var(--cor-borda)")
            ):
                ui.label("Conecte-se para começar").classes("text-lg font-semibold mb-4")
                ui.label("Configure o Elasticsearch e o LLM na barra lateral para iniciar.").classes(
                    "text-sm text-grey-7"
                )

    def renderizar_selecao_indice() -> None:
        """Renderiza tela de seleção de índice (conectado, sem índice)."""
        with ui.column().classes("w-full items-center justify-center min-h-[70vh] gap-4"):
            ui.icon("search", size="4rem", color="grey-5")
            ui.html('<div class="landing-titulo" style="font-size: 1.8rem;">Selecione um índice</div>')
            ui.html('<div class="landing-subtitulo">Escolha o índice na barra lateral para iniciar o chat.</div>')

    def renderizar_chat() -> None:
        """Renderiza a interface de chat."""
        with ui.column().classes("w-full h-full"):
            # Área de mensagens rolável
            with ui.scroll_area().classes("flex-grow w-full area-rolagem").style("height: calc(100vh - 180px)"):
                refs["container_chat"] = ui.column().classes("chat-container w-full py-4")

                with refs["container_chat"]:
                    # Mensagem de boas-vindas
                    if not estado.mensagens_chat:
                        with ui.column().classes("w-full items-center justify-center py-12 gap-4"):
                            ui.icon("chat_bubble_outline", size="3rem", color="grey-4")
                            ui.label("Pergunte algo sobre seus dados").classes("text-xl font-semibold text-grey-7")
                            ui.label(f"Índice: {estado.indice_selecionado}").classes("text-sm text-grey-5")

                            # Chips de sugestão
                            sugestoes = obter_sugestoes(estado.indice_selecionado)
                            if sugestoes:
                                with ui.row().classes("flex-wrap justify-center gap-2 mt-4"):
                                    for sugestao in sugestoes:
                                        ui.button(
                                            sugestao,
                                            on_click=lambda s=sugestao: ao_enviar_mensagem(s),
                                        ).props("flat no-caps").classes("chip-sugestao")
                    else:
                        # Re-renderiza mensagens existentes
                        for msg in estado.mensagens_chat:
                            renderizar_mensagem(msg["papel"], msg["conteudo"])

            # Campo de entrada fixo na parte inferior
            with ui.row().classes("w-full p-3 campo-entrada items-center gap-2"):
                refs["entrada_texto"] = (
                    ui.input(
                        placeholder=f"Pergunte algo sobre {estado.indice_selecionado}...",
                    )
                    .props("outlined dense")
                    .classes("flex-grow")
                    .on("keydown.enter", lambda: ao_enviar_mensagem())
                )
                ui.button(
                    icon="send",
                    on_click=lambda: ao_enviar_mensagem(),
                ).props("round flat color=primary").style("color: var(--cor-primaria)")

    # ====== Layout principal ======

    ui.add_css(CSS_PERSONALIZADO)

    # Sidebar (gaveta lateral) — declarada antes do header para que a referência exista no lambda
    gaveta = ui.left_drawer(value=True, bordered=True).classes("p-4")

    # Cabeçalho
    with ui.header().classes("items-center px-4 py-2 shadow-none"):
        ui.button(icon="menu", on_click=lambda: gaveta.toggle()).props("flat round color=grey-8")
        ui.label("AgnostiChat").classes("text-lg font-bold ml-2").style("color: var(--cor-texto)")
        ui.space()
        if estado.conectado:
            with ui.row().classes("items-center gap-1"):
                ui.html('<span class="indicador-status status-conectado"></span>')
                ui.label("Conectado").classes("text-xs text-grey-6")
        else:
            with ui.row().classes("items-center gap-1"):
                ui.html('<span class="indicador-status status-desconectado"></span>')
                ui.label("Desconectado").classes("text-xs text-grey-6")

    # Conteúdo da sidebar
    with gaveta:
        # Logo e título
        with ui.column().classes("items-center mb-6"):
            ui.image("assets/logo_agnostic.png").classes("w-16 h-16")
            ui.label("AgnostiChat").classes("text-lg font-bold mt-2").style("color: var(--cor-primaria)")
            ui.label("powered by AgnosticData").classes("text-xs text-grey-6")

        # Configuração Elasticsearch
        with ui.element("div").classes("cartao-config"):
            ui.label("Elasticsearch").classes("text-sm font-semibold mb-2")
            ui.input(
                "Host",
                value=estado.es_host,
                placeholder="http://localhost:9200",
                on_change=lambda e: setattr(estado, "es_host", e.value),
            ).props("outlined dense").classes("w-full mb-2")
            ui.input(
                "API Key",
                value=estado.es_api_key,
                placeholder="Opcional",
                password=True,
                password_toggle_button=True,
                on_change=lambda e: setattr(estado, "es_api_key", e.value),
            ).props("outlined dense").classes("w-full mb-3")
            ui.button("Conectar", on_click=ao_conectar).classes("w-full botao-conectar").props("no-caps")

        # Configuração LLM
        with ui.element("div").classes("cartao-config"):
            ui.label("LLM Provider").classes("text-sm font-semibold mb-2")
            ui.select(
                ["openai", "ollama (local)"],
                value=estado.llm_provider,
                on_change=lambda e: setattr(estado, "llm_provider", e.value),
            ).props("outlined dense").classes("w-full mb-2")
            ui.input(
                "API Key do LLM",
                value=estado.llm_api_key,
                placeholder="Cole sua chave aqui",
                password=True,
                password_toggle_button=True,
                on_change=lambda e: setattr(estado, "llm_api_key", e.value),
            ).props("outlined dense").classes("w-full")

        # Seleção de índice (aparece apenas quando conectado)
        if estado.conectado and estado.indices:
            with ui.element("div").classes("cartao-config"):
                ui.label("Índice").classes("text-sm font-semibold mb-2")
                ui.select(
                    estado.indices,
                    value=estado.indice_selecionado,
                    on_change=lambda e: ao_selecionar_indice(e.value),
                ).props("outlined dense").classes("w-full")

    # Área de conteúdo principal
    with ui.column().classes("w-full h-full"):
        refs["container_principal"] = ui.column().classes("w-full h-full")
        with refs["container_principal"]:
            renderizar_landing()


def _montar_prompt_interpretacao(
    pergunta: str,
    query_dsl_json: str,
    resultado: dict,
    tem_aggs: bool,
    tem_hits: bool,
) -> str:
    """Monta o prompt de interpretação dos resultados do Elasticsearch."""
    if tem_aggs and tem_hits:
        return (
            f"Pergunta do usuário:\n{pergunta}\n\n"
            f"Query DSL executada:\n{query_dsl_json}\n\n"
            f"Resultado de agregação retornado do Elasticsearch:\n"
            f"{json.dumps(resultado['aggregations'], ensure_ascii=False, indent=2)}\n\n"
            f"Documentos retornados (até 10 exemplos):\n"
            f"{json.dumps(resultado['hits']['hits'][:10], ensure_ascii=False, indent=2)}\n\n"
            "IMPORTANTE:\n"
            "- Se a agregação não trouxer resultado, analise os documentos e extraia a resposta.\n"
            "- Liste os valores únicos do campo mais relevante para a pergunta.\n"
            "- Responda de forma clara e objetiva."
        )
    if tem_aggs:
        return (
            f"Pergunta do usuário:\n{pergunta}\n\n"
            f"Query DSL executada:\n{query_dsl_json}\n\n"
            f"Resultado de agregação retornado do Elasticsearch:\n"
            f"{json.dumps(resultado['aggregations'], ensure_ascii=False, indent=2)}\n\n"
            "Explique de forma resumida e clara o que significa esse resultado para o usuário."
        )
    if tem_hits:
        exemplos = resultado["hits"]["hits"][:10]
        return (
            f"Pergunta do usuário:\n{pergunta}\n\n"
            f"Query DSL executada:\n{query_dsl_json}\n\n"
            f"Documentos retornados (até 10 exemplos):\n"
            f"{json.dumps(exemplos, ensure_ascii=False, indent=2)}\n\n"
            "IMPORTANTE:\n"
            "- Liste os valores únicos do campo mais relevante para a pergunta.\n"
            "- Responda de forma clara e objetiva."
        )
    return (
        f"Pergunta do usuário:\n{pergunta}\n\n"
        f"Query DSL executada:\n{query_dsl_json}\n\n"
        "Nenhum resultado retornado do Elasticsearch."
    )


# ====== Ponto de entrada ======
porta = int(os.getenv("PORT", "8080"))
ui.run(
    title="AgnostiChat",
    host="0.0.0.0",
    port=porta,
    storage_secret="agnostichat-secret-key",
    dark=False,
    favicon="assets/logo_agnostic.png",
)
