"""CSS personalizado da aplicação AgnostiChat."""

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
