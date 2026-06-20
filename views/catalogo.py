"""Catalogo de animais disponiveis para adocao (visao do cliente)."""
from __future__ import annotations

from contextlib import closing

import streamlit as st

from app import ui
from db.connection import get_connection
from models.entities import rotulo
from services import file_storage, servico_animais


def _filtrar_por_especie(animais, especie):
    filtrados = []
    for animal in animais:
        if animal["especie"] == especie:
            filtrados.append(animal)
    return filtrados


def render() -> None:
    ui.hero(
        "Animais para adoção",
        "Conheça quem está esperando por um novo lar e um pouco de carinho.",
    )

    with closing(get_connection()) as conn:
        animais = servico_animais.listar_disponiveis(conn)

    col1, _ = st.columns([1, 3])
    with col1:
        filtro = st.selectbox("Filtrar por espécie", ["Todas", "Cão", "Gato"])

    if filtro == "Cão":
        animais = _filtrar_por_especie(animais, "cao")
    elif filtro == "Gato":
        animais = _filtrar_por_especie(animais, "gato")

    if not animais:
        st.info("Nenhum animal disponível no momento. Volte em breve.")
        return

    st.caption(f"{len(animais)} animal(is) disponível(is) para adoção.")
    colunas = st.columns(3)
    for i, animal in enumerate(animais):
        with colunas[i % 3]:
            with st.container(border=True):
                caminho = animal["caminho_foto"]
                if file_storage.arquivo_existe(caminho):
                    st.image(str(file_storage.caminho_absoluto(caminho)), use_container_width=True)
                else:
                    st.markdown(
                        "<div style='height:150px;border-radius:12px;"
                        "background:linear-gradient(135deg,#FFE3D3,#FFF1E6);"
                        "display:flex;align-items:center;justify-content:center;"
                        "color:#C58B6F;font-weight:700;'>Sem foto</div>",
                        unsafe_allow_html=True,
                    )
                st.markdown(f"### {animal['nome']}")
                st.markdown(ui.badge_status(animal["status"]), unsafe_allow_html=True)
                st.write(
                    f"**Espécie:** {rotulo('especie', animal['especie'])}  \n"
                    f"**Sexo:** {rotulo('sexo', animal['sexo'])}  \n"
                    f"**Idade:** {animal['idade']} ano(s)  \n"
                    f"**Raça:** {animal['raca'] or 'SRD'}"
                )
                if animal["descricao"]:
                    st.caption(animal["descricao"])
