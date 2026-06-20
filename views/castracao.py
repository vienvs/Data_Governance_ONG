"""Solicitacao de castracao e acompanhamento (visao do usuario)."""
from __future__ import annotations

from contextlib import closing

import streamlit as st

from app import session, ui
from db.connection import get_connection
from models.entities import rotulo
from services import servico_castracao
from services.errors import ErroDominio
from services.validators import campos_obrigatorios_ausentes


def render() -> None:
    usuario = session.requer_autenticacao()
    ui.hero("Castração", "Solicite a castração do seu pet. A ONG analisa e agenda o procedimento.")

    aba_nova, aba_minhas = st.tabs(["Solicitar castração", "Minhas solicitações"])
    with aba_nova:
        _form_solicitar(usuario)
    with aba_minhas:
        _minhas_solicitacoes(usuario)


def _form_solicitar(usuario) -> None:
    with st.form("solicitar_castracao"):
        nome_pet = st.text_input("Nome do pet")
        col1, col2 = st.columns(2)
        with col1:
            especie = st.selectbox("Espécie", ["cao", "gato"],
                                   format_func=lambda v: rotulo("especie", v))
            idade_pet = st.number_input("Idade (anos)", min_value=0, max_value=40, step=1)
        with col2:
            sexo = st.selectbox("Sexo", ["macho", "femea"],
                                format_func=lambda v: rotulo("sexo", v))
        nome_tutor = st.text_input("Nome do tutor", value=usuario.nome)
        telefone = st.text_input("Telefone")
        endereco = st.text_input("Endereço")
        enviar = st.form_submit_button("Solicitar")

    if enviar:
        faltando = campos_obrigatorios_ausentes(
            {"nome_pet": nome_pet, "nome_tutor": nome_tutor,
             "telefone": telefone, "endereco": endereco},
            ["nome_pet", "nome_tutor", "telefone", "endereco"],
        )
        if faltando:
            st.error("Preencha: " + ", ".join(faltando))
            return
        try:
            with closing(get_connection()) as conn:
                servico_castracao.solicitar_castracao(
                    conn, usuario.id, nome_pet, especie, sexo, idade_pet,
                    nome_tutor, telefone, endereco,
                )
            st.success("Solicitação de castração registrada!")
        except ErroDominio as e:
            st.error(e.mensagem_usuario)


def _minhas_solicitacoes(usuario) -> None:
    with closing(get_connection()) as conn:
        solicitacoes = servico_castracao.listar_do_usuario(conn, usuario.id)
    if not solicitacoes:
        st.info("Você ainda não solicitou nenhuma castração.")
        return
    for s in solicitacoes:
        with st.container(border=True):
            agenda = s["data_agendada"]
            st.markdown(f"**Pet:** {s['nome_pet']} ({rotulo('especie', s['especie'])})")
            st.markdown(ui.badge_status(s["status"]), unsafe_allow_html=True)
            st.caption(f"Agendada para: {agenda if agenda else 'a definir'}")
