"""Estilo visual da aplicacao.

Centraliza o CSS e alguns componentes visuais reutilizaveis (hero, badge),
para deixar a interface com aparencia de site, com animacoes suaves.
"""
from __future__ import annotations

import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Nunito', sans-serif;
}

.main .block-container {
    animation: fadeIn 0.6s ease;
    padding-top: 2rem;
    max-width: 1100px;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}

@keyframes pop {
    0%   { transform: scale(0.96); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
}

.hero {
    background: linear-gradient(135deg, #F4845F 0%, #FFB088 100%);
    color: #ffffff;
    padding: 2.4rem 2.2rem;
    border-radius: 22px;
    margin-bottom: 1.6rem;
    box-shadow: 0 12px 32px rgba(244, 132, 95, 0.35);
    animation: pop 0.5s ease;
}
.hero h1 {
    color: #ffffff;
    margin: 0 0 0.4rem 0;
    font-weight: 800;
    font-size: 2.1rem;
    letter-spacing: -0.5px;
}
.hero p {
    margin: 0;
    font-size: 1.08rem;
    opacity: 0.96;
}

.badge {
    display: inline-block;
    padding: 0.18rem 0.7rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.2px;
}
.badge-ok   { background: #E6F4EA; color: #1E7D34; }
.badge-wait { background: #FFF3D6; color: #9A6B00; }
.badge-no   { background: #FDE7E7; color: #B42318; }

.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    border: none;
    padding: 0.5rem 1.1rem;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px !important;
    border: 1px solid #FFE3D3 !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
    transition: transform 0.16s ease, box-shadow 0.16s ease;
    background: #ffffff;
}
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.10);
}

div[data-testid="stImage"] img {
    border-radius: 12px;
}

h1, h2, h3 { color: #3A2E2A; }

section[data-testid="stSidebar"] {
    background: #FFF1E6;
}
section[data-testid="stSidebar"] .block-container { padding-top: 1.2rem; }
</style>
"""


def aplicar_estilo() -> None:
    """Injeta o CSS global. Deve ser chamada uma vez por pagina."""
    st.markdown(_CSS, unsafe_allow_html=True)


def hero(titulo: str, subtitulo: str = "") -> None:
    """Renderiza um cabecalho de destaque com gradiente."""
    html = f"<div class='hero'><h1>{titulo}</h1>"
    if subtitulo:
        html += f"<p>{subtitulo}</p>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def badge(texto: str, tipo: str = "ok") -> str:
    """Devolve o HTML de um selo colorido (ok, wait, no)."""
    classe = {"ok": "badge-ok", "wait": "badge-wait", "no": "badge-no"}.get(tipo, "badge-ok")
    return f"<span class='badge {classe}'>{texto}</span>"


def badge_status(status: str) -> str:
    """Selo a partir do status de aprovacao ou de animal."""
    mapa = {
        "aprovado": ("Aprovado", "ok"),
        "disponivel": ("Disponível", "ok"),
        "em_analise": ("Em análise", "wait"),
        "reprovado": ("Reprovado", "no"),
        "adotado": ("Adotado", "ok"),
    }
    texto, tipo = mapa.get(status, (status, "ok"))
    return badge(texto, tipo)
