"""Página principal, roteamento e handlers de eventos da aplicação NiceGUI."""

from __future__ import annotations

import asyncio
import json
from functools import partial
from pathlib import Path

from nicegui import app, ui

from agnostichat.services.elasticsearch_utils import (
    buscar_amostras,
    buscar_mapping,
    conectar_elasticsearch,
    listar_indices,
)
from agnostichat.services.llm_utils import validar_llm
from agnostichat.ui.chat import processar_pergunta
from agnostichat.ui.components import (
    renderizar_chat,
    renderizar_header,
    renderizar_landing,
    renderizar_mensagem,
    renderizar_selecao_indice,
    renderizar_sidebar,
    renderizar_status,
)
from agnostichat.ui.state import EstadoApp
from agnostichat.ui.styles import CSS_PERSONALIZADO

# Registra diretório de assets estáticos
_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
app.add_static_files("/assets", str(_ASSETS_DIR))


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
            basic_auth = (estado.es_user, estado.es_password) if estado.es_user and estado.es_password else None
            estado.es_client = conectar_elasticsearch(estado.es_host, estado.es_api_key or None, basic_auth)
            estado.conectado = True
            estado.indices = listar_indices(estado.es_client)
            ui.notify(f"Conectado! {len(estado.indices)} índices encontrados.", type="positive")
            atualizar_interface()
        except Exception as e:
            estado.conectado = False
            estado.es_client = None
            ui.notify(f"Erro ao conectar: {e}", type="negative")

    async def ao_validar_llm() -> None:
        """Valida a conexão com o LLM."""
        if not estado.llm_api_key and estado.llm_provider == "openai":
            ui.notify("Informe a API Key do LLM", type="warning")
            return
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, partial(validar_llm, estado.llm_api_key, estado.llm_provider)
            )
            estado.llm_validado = True
            ui.notify("LLM validado com sucesso!", type="positive")
            atualizar_interface()
        except Exception as e:
            estado.llm_validado = False
            ui.notify(f"Erro ao validar LLM: {e}", type="negative")

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
        if not estado.llm_validado:
            ui.notify("Valide a conexão com o LLM antes de enviar perguntas.", type="warning")
            return
        texto = pergunta or (refs["entrada_texto"].value if refs["entrada_texto"] else None)
        if not texto or not texto.strip():
            return
        if refs["entrada_texto"]:
            refs["entrada_texto"].value = ""

        # Adiciona mensagem do usuário
        estado.mensagens_chat.append({"papel": "usuario", "conteudo": texto})
        renderizar_mensagem(refs["container_chat"], "usuario", texto)

        # Indicador de carregamento
        with refs["container_chat"]:
            carregando = ui.row().classes("items-center gap-2 p-3")
            with carregando:
                ui.spinner("dots", size="sm", color="grey")
                ui.label("Gerando consulta...").classes("text-grey-6 text-sm")

        # Rola para baixo
        await ui.run_javascript("document.querySelector('.area-rolagem')?.scrollTo({top: 999999, behavior: 'smooth'})")

        try:
            conteudo_resposta = await asyncio.get_event_loop().run_in_executor(
                None, partial(processar_pergunta, estado, texto)
            )

            # Remove indicador de carregamento e mostra resposta
            carregando.delete()
            estado.mensagens_chat.append({"papel": "assistente", "conteudo": conteudo_resposta})
            renderizar_mensagem(refs["container_chat"], "assistente", conteudo_resposta)

        except json.JSONDecodeError:
            carregando.delete()
            msg_erro = "Não foi possível interpretar a query DSL gerada. Tente reformular sua pergunta."
            estado.mensagens_chat.append({"papel": "assistente", "conteudo": {"texto": msg_erro}})
            renderizar_mensagem(refs["container_chat"], "assistente", {"texto": msg_erro})

        except Exception as e:
            carregando.delete()
            msg_erro = f"Erro no processamento: {e}"
            estado.mensagens_chat.append({"papel": "assistente", "conteudo": {"texto": msg_erro}})
            renderizar_mensagem(refs["container_chat"], "assistente", {"texto": msg_erro})

        # Rola para baixo
        await ui.run_javascript("document.querySelector('.area-rolagem')?.scrollTo({top: 999999, behavior: 'smooth'})")

    def atualizar_interface() -> None:
        """Reconstrói a área principal, sidebar e header com base no estado atual."""
        refs["container_principal"].clear()
        with refs["container_principal"]:
            if not estado.conectado:
                renderizar_landing()
            elif not estado.chat_iniciado:
                renderizar_selecao_indice()
            else:
                renderizar_chat(estado, refs, ao_enviar_mensagem)

        # Atualiza sidebar (mostra seletor de índice após conexão)
        refs["container_sidebar"].clear()
        with refs["container_sidebar"]:
            renderizar_sidebar(estado, ao_conectar, ao_selecionar_indice, ao_validar_llm)

        # Atualiza indicador de status no header
        renderizar_status(refs["container_status"], estado)

    # ====== Layout principal ======

    ui.add_css(CSS_PERSONALIZADO)

    # Sidebar (gaveta lateral) — declarada antes do header para que a referência exista no lambda
    gaveta = ui.left_drawer(value=True, bordered=True).classes("p-4")

    # Cabeçalho
    refs["container_status"] = renderizar_header(estado, gaveta)

    # Conteúdo da sidebar (dentro de um container para permitir atualização)
    with gaveta:
        refs["container_sidebar"] = ui.column().classes("w-full")
        with refs["container_sidebar"]:
            renderizar_sidebar(estado, ao_conectar, ao_selecionar_indice, ao_validar_llm)

    # Área de conteúdo principal
    with ui.column().classes("w-full h-full"):
        refs["container_principal"] = ui.column().classes("w-full h-full")
        with refs["container_principal"]:
            renderizar_landing()
