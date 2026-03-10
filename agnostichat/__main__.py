"""Ponto de entrada: python -m agnostichat."""

# Importa o módulo de app para registrar páginas e arquivos estáticos
from nicegui import ui

import agnostichat.ui.app as _app  # noqa: F401
from agnostichat.config import Configuracao

_config = Configuracao()
ui.run(
    title="AgnostiChat",
    host="0.0.0.0",
    port=_config.porta,
    storage_secret=_config.storage_secret,
    dark=False,
    favicon="/assets/logo_agnostichat.png",
    reload=False,
)
