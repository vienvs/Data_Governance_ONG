"""Catalogo de animais disponiveis para adocao (visao do cliente)."""
from __future__ import annotations

from contextlib import closing

import streamlit as st

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
    st.title("Animais disponiveis para adocao")
    st.caption("Conheca os animais que estao esperando por um novo lar.")

    with closing(get_connection()) as conn:
        animais = servico_animais.listar_disponiveis(conn)

    # filtro simples por especie
    col1, col2 = st.columns([1, 3])
    with col1:
        filtro = st.selectbox("Especie", ["Todas", "Cao", "Gato"])

    if filtro == "Cao":
        animais = _filtrar_por_especie(animais, "cao")
    elif filtro == "Gato":
        animais = _filtrar_por_especie(animais, "gato")

    if not animais:
        st.info("Nenhum animal disponivel no momento.")
        return

    colunas = st.columns(3)
    for i, animal in enumerate(animais):
        with colunas[i % 3]:
            with st.container(border=True):
                caminho = animal["caminho_foto"]
                if file_storage.arquivo_existe(caminho):
                    st.image(str(file_storage.caminho_absoluto(caminho)), use_container_width=True)
                else:
                    st.markdown("*(sem foto)*")
                st.subheader(animal["nome"])
                st.write(
                    f"**Especie:** {rotulo('especie', animal['especie'])}  \n"
                    f"**Sexo:** {rotulo('sexo', animal['sexo'])}  \n"
                    f"**Idade:** {animal['idade']} ano(s)  \n"
                    f"**Raca:** {animal['raca'] or 'SRD'}"
                )
                if animal["descricao"]:
                    st.caption(animal["descricao"])
