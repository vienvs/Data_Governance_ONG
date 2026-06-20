"""Estilo visual da aplicacao.

Design minimalista e plano (sem degrades), com formas mais retas, fonte Inter
e tema claro/escuro. Centraliza o CSS e componentes visuais reutilizaveis.
"""
from __future__ import annotations

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css');

:root {
    --cor-primaria: #E2643C;
    --cor-texto: #1F1B18;
    --cor-suave: #6B635D;
    --cor-borda: #E6E0DB;
    --cor-superficie: #FFFFFF;
    --cor-fundo: #FBFAF9;
}

html, body, [class*="css"], .stApp,
input, textarea, button, select {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.stApp { background-color: var(--cor-fundo); }

.main .block-container {
    padding-top: 2rem;
    max-width: 1080px;
}

/* Barra superior do Streamlit */
[data-testid="stHeader"] {
    background: var(--cor-fundo);
    border-bottom: 1px solid var(--cor-borda);
}

/* Cabecalho de pagina (plano, sem degrade) */
.cabecalho {
    padding: 0.2rem 0 1rem 0;
    margin-bottom: 1.4rem;
    border-bottom: 1px solid var(--cor-borda);
}
.cabecalho .titulo {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--cor-texto);
    display: flex;
    align-items: center;
    gap: 0.55rem;
}
.cabecalho .titulo i { color: var(--cor-primaria); font-size: 1.6rem; }
.cabecalho .sub { color: var(--cor-suave); font-size: 1rem; margin-top: 0.25rem; }

h1, h2, h3, h4 { color: var(--cor-texto); letter-spacing: -0.01em; }

/* Selos de status (retos) */
.selo {
    display: inline-block;
    padding: 0.12rem 0.55rem;
    border-radius: 4px;
    font-size: 0.76rem;
    font-weight: 600;
    border: 1px solid transparent;
}
.selo-ok   { background: #EAF4EC; color: #1E7D34; border-color: #CBE6D1; }
.selo-wait { background: #FBF1D9; color: #8A5D00; border-color: #EBDBB0; }
.selo-no   { background: #FBE6E5; color: #B42318; border-color: #F0CBC8; }

/* Botoes planos e retos */
.stButton > button {
    border-radius: 6px;
    font-weight: 600;
    border: 1px solid var(--cor-primaria);
    background: var(--cor-primaria);
    color: #FFFFFF;
    padding: 0.45rem 1rem;
    transition: filter 0.12s ease;
}
.stButton > button:hover { filter: brightness(0.94); color: #FFFFFF; }

/* Cartoes: borda fina, cantos discretos, sem sombra/elevacao */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 8px !important;
    border: 1px solid var(--cor-borda) !important;
    background: var(--cor-superficie);
}

div[data-testid="stImage"] img { border-radius: 6px; }

/* Campos de formulario retos */
.stTextInput input, .stNumberInput input, .stDateInput input, textarea,
div[data-baseweb="select"] > div {
    border-radius: 6px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--cor-superficie);
    border-right: 1px solid var(--cor-borda);
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }

.link-rodape {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    text-decoration: none;
    font-weight: 600;
    color: var(--cor-primaria);
}
.link-rodape i { font-size: 1.05rem; }
</style>
"""

_CSS_ESCURO = """
<style>
:root {
    --cor-texto: #ECE6E1;
    --cor-suave: #A89F98;
    --cor-borda: #322C26;
    --cor-superficie: #211D19;
    --cor-fundo: #161311;
}
.stApp { background-color: var(--cor-fundo); }
[data-testid="stHeader"] { background: var(--cor-fundo); border-bottom: 1px solid var(--cor-borda); }
[data-testid="stToolbar"] { color: var(--cor-texto); }

.stApp, .main .block-container, p, li, label, .stMarkdown,
[data-testid="stWidgetLabel"], [data-testid="stMarkdownContainer"] {
    color: var(--cor-texto);
}
h1, h2, h3, h4, .cabecalho .titulo { color: var(--cor-texto); }
.cabecalho .sub, [data-testid="stCaptionContainer"], .stCaption { color: var(--cor-suave) !important; }

section[data-testid="stSidebar"] { background: var(--cor-superficie); border-right: 1px solid var(--cor-borda); }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--cor-superficie) !important;
    border-color: var(--cor-borda) !important;
}
div[data-testid="stExpander"], div[data-testid="stExpander"] details {
    background: var(--cor-superficie) !important;
    border-color: var(--cor-borda) !important;
}

.stTextInput input, .stNumberInput input, .stDateInput input, textarea,
div[data-baseweb="select"] > div {
    background-color: #2A241F !important;
    color: var(--cor-texto) !important;
    border-color: var(--cor-borda) !important;
}
.stTabs [data-baseweb="tab"] { color: var(--cor-texto); }
</style>
"""


def aplicar_estilo(escuro: bool = False) -> None:
    """Injeta o CSS global. Se escuro for True, aplica o tema escuro por cima."""
    st.markdown(_CSS, unsafe_allow_html=True)
    if escuro:
        st.markdown(_CSS_ESCURO, unsafe_allow_html=True)


def cabecalho(titulo: str, subtitulo: str = "", icone: str | None = None) -> None:
    """Cabecalho de pagina plano (sem degrade), com icone opcional."""
    icone_html = f"<i class='bi bi-{icone}'></i>" if icone else ""
    html = f"<div class='cabecalho'><div class='titulo'>{icone_html}{titulo}</div>"
    if subtitulo:
        html += f"<div class='sub'>{subtitulo}</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# Mantem compatibilidade com chamadas existentes (hero == cabecalho).
def hero(titulo: str, subtitulo: str = "", icone: str | None = None) -> None:
    cabecalho(titulo, subtitulo, icone)


def badge(texto: str, tipo: str = "ok") -> str:
    classe = {"ok": "selo-ok", "wait": "selo-wait", "no": "selo-no"}.get(tipo, "selo-ok")
    return f"<span class='selo {classe}'>{texto}</span>"


def badge_status(status: str) -> str:
    mapa = {
        "aprovado": ("Aprovado", "ok"),
        "disponivel": ("Disponível", "ok"),
        "em_analise": ("Em análise", "wait"),
        "reprovado": ("Reprovado", "no"),
        "adotado": ("Adotado", "ok"),
    }
    texto, tipo = mapa.get(status, (status, "ok"))
    return badge(texto, tipo)


def estilos_menu(escuro: bool = False) -> dict:
    """Estilos do option_menu, adaptados ao tema (claro/escuro)."""
    if escuro:
        texto = "#ECE6E1"
        hover = "#2C2620"
    else:
        texto = "#1F1B18"
        hover = "#F2ECE7"
    return {
        "container": {"background-color": "transparent", "padding": "0"},
        "icon": {"color": "#E2643C", "font-size": "16px"},
        "nav-link": {
            "font-size": "14px",
            "font-weight": "600",
            "color": texto,
            "border-radius": "6px",
            "margin": "2px 0",
            "--hover-color": hover,
        },
        "nav-link-selected": {"background-color": "#E2643C", "color": "#FFFFFF"},
    }
