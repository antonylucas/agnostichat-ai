"""Componentes reutilizáveis de renderização da interface NiceGUI."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from nicegui import ui

from agnostichat.ui.chat import obter_sugestoes
from agnostichat.ui.state import EstadoApp


def renderizar_mensagem(container: Any, papel: str, conteudo: str | dict) -> None:
    """Renderiza uma mensagem no container do chat."""
    with container:
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


def renderizar_landing() -> None:
    """Renderiza a página de landing (não conectado)."""
    with ui.column().classes("w-full items-center justify-center min-h-[70vh] gap-6"):
        ui.image("/assets/logo_agnostichat.png").classes("w-48 opacity-90")
        ui.html(
            '<div class="landing-subtitulo" style="margin-top: -8px;">'
            "Interface conversacional para Elasticsearch com IA"
            "</div>"
        )
        with (
            ui.card()
            .classes("w-full max-w-md p-6 mt-4")
            .style("border-radius: 16px; border: 1px solid var(--cor-borda)")
        ):
            ui.label("Conecte-se para começar").classes("text-lg font-semibold mb-4")
            ui.label("Configure o Elasticsearch e o LLM na barra lateral para iniciar.").classes("text-sm text-grey-7")


def renderizar_selecao_indice() -> None:
    """Renderiza tela de seleção de índice (conectado, sem índice)."""
    with ui.column().classes("w-full items-center justify-center min-h-[70vh] gap-4"):
        ui.icon("search", size="4rem", color="grey-5")
        ui.html('<div class="landing-titulo" style="font-size: 1.8rem;">Selecione um índice</div>')
        ui.html('<div class="landing-subtitulo">Escolha o índice na barra lateral para iniciar o chat.</div>')


def renderizar_chat(
    estado: EstadoApp,
    refs: dict,
    ao_enviar_mensagem: Callable,
) -> None:
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
                        renderizar_mensagem(refs["container_chat"], msg["papel"], msg["conteudo"])

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


def renderizar_sidebar(
    estado: EstadoApp, ao_conectar: Callable, ao_selecionar_indice: Callable, ao_validar_llm: Callable | None = None
) -> None:
    """Renderiza o conteúdo da sidebar."""
    # Logo
    with ui.column().classes("items-center mb-4"):
        ui.image("/assets/logo_agnostichat.png").classes("w-36")

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
            "Usuário",
            value=estado.es_user,
            placeholder="Opcional",
            on_change=lambda e: setattr(estado, "es_user", e.value),
        ).props("outlined dense").classes("w-full mb-2")
        ui.input(
            "Senha",
            value=estado.es_password,
            placeholder="Opcional",
            password=True,
            password_toggle_button=True,
            on_change=lambda e: setattr(estado, "es_password", e.value),
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
        ).props("outlined dense").classes("w-full mb-3")
        if ao_validar_llm:
            if estado.llm_validado:
                ui.button("LLM Validado", on_click=ao_validar_llm).classes("w-full botao-conectar").props(
                    "no-caps color=positive"
                )
            else:
                ui.button("Validar LLM", on_click=ao_validar_llm).classes("w-full botao-conectar").props("no-caps")

    # Seleção de índice (aparece apenas quando conectado)
    if estado.conectado and estado.indices:
        with ui.element("div").classes("cartao-config"):
            ui.label("Índice").classes("text-sm font-semibold mb-2")
            ui.select(
                estado.indices,
                value=estado.indice_selecionado,
                on_change=lambda e: ao_selecionar_indice(e.value),
            ).props("outlined dense").classes("w-full")


def renderizar_status(container: Any, estado: EstadoApp) -> None:
    """Atualiza o indicador de status de conexão no header."""
    container.clear()
    with container:
        if estado.conectado:
            with ui.row().classes("items-center gap-1"):
                ui.html('<span class="indicador-status status-conectado"></span>')
                ui.label("Conectado").classes("text-xs text-grey-6")
        else:
            with ui.row().classes("items-center gap-1"):
                ui.html('<span class="indicador-status status-desconectado"></span>')
                ui.label("Desconectado").classes("text-xs text-grey-6")


def renderizar_header(estado: EstadoApp, gaveta: Any) -> Any:
    """Renderiza o cabeçalho da aplicação. Retorna o container de status."""
    with ui.header().classes("items-center px-4 py-2 shadow-none"):
        ui.button(icon="menu", on_click=lambda: gaveta.toggle()).props("flat round color=grey-8")
        ui.label("AgnostiChat").classes("text-lg font-bold ml-2").style("color: var(--cor-texto)")
        ui.space()
        container_status = ui.row()
        renderizar_status(container_status, estado)
    return container_status
