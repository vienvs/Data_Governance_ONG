"""Solicitacao de adocao (com questionario) e acompanhamento das proprias solicitacoes."""
from __future__ import annotations

from contextlib import closing

import streamlit as st

from app import session, ui
from db.connection import get_connection
from models.entities import rotulo
from services import servico_adocao, servico_animais, servico_perfil_dono
from services.errors import ErroDominio

PERGUNTAS = [
    "Todos os membros da família estão de acordo com a adoção?",
    "Por que você deseja adotar este animal?",
    "Você já teve outros animais? Como foi a experiência?",
    "Quem ficará responsável pelos cuidados e custos do animal?",
]


def render() -> None:
    usuario = session.requer_autenticacao()
    ui.hero("Adoção", "Solicite a adoção de um animal disponível e acompanhe o status.")

    with closing(get_connection()) as conn:
        perfil = servico_perfil_dono.obter_perfil_por_usuario(conn, usuario.id)

    if perfil is None:
        st.warning("Você precisa completar seu perfil de adotante antes de solicitar uma adoção.")
        st.info("Use o menu lateral: **Meu perfil**.")
        return

    aba_nova, aba_minhas = st.tabs(["Solicitar adoção", "Minhas solicitações"])

    with aba_nova:
        _form_solicitar(usuario, perfil)
    with aba_minhas:
        _minhas_solicitacoes(perfil)


def _form_solicitar(usuario, perfil) -> None:
    with closing(get_connection()) as conn:
        disponiveis = servico_animais.listar_disponiveis(conn)

    if not disponiveis:
        st.info("Não há animais disponíveis para adoção no momento.")
        return

    opcoes = {}
    for a in disponiveis:
        rotulo_animal = f"{a['nome']} ({rotulo('especie', a['especie'])})"
        opcoes[rotulo_animal] = a["id"]
    with st.form("solicitar_adocao"):
        escolha = st.selectbox("Animal", list(opcoes.keys()))
        st.markdown("**Questionário de entrevista:**")
        respostas = {}
        for i, pergunta in enumerate(PERGUNTAS):
            respostas[pergunta] = st.text_area(pergunta, key=f"perg_{i}")
        enviar = st.form_submit_button("Enviar solicitação")

    if enviar:
        try:
            with closing(get_connection()) as conn:
                servico_adocao.solicitar_adocao(conn, perfil["id"], opcoes[escolha], respostas)
            st.success("Solicitação enviada! Acompanhe o status na aba 'Minhas solicitações'.")
        except ErroDominio as e:
            st.error(e.mensagem_usuario)


def _minhas_solicitacoes(perfil) -> None:
    with closing(get_connection()) as conn:
        solicitacoes = servico_adocao.listar_solicitacoes_do_dono(conn, perfil["id"])
    if not solicitacoes:
        st.info("Você ainda não fez nenhuma solicitação.")
        return
    for s in solicitacoes:
        with st.container(border=True):
            st.markdown(f"**Animal:** {s['nome_animal']}")
            st.markdown(ui.badge_status(s["status"]), unsafe_allow_html=True)
            st.caption(f"Data: {s['data_solicitacao']}")
            if s["observacoes_admin"]:
                st.caption(f"Observações da ONG: {s['observacoes_admin']}")
