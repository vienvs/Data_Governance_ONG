"""Telas de autenticacao: login e cadastro."""
from __future__ import annotations

from contextlib import closing
from datetime import date

import streamlit as st

from app import session, ui
from db.connection import get_connection
from services import servico_autenticacao, servico_cadastro_usuario
from services.errors import ErroDominio
from services.validators import campos_obrigatorios_ausentes


def render() -> None:
    ui.hero(
        "Bem-vindo à Adota Pet SJC e RonRon",
        "Conectamos cães e gatos a lares responsáveis em São José dos Campos. Entre ou crie sua conta para começar.",
        icone="house-heart",
    )

    col_form, col_info = st.columns([3, 2])
    with col_form:
        aba_login, aba_cadastro = st.tabs(["Entrar", "Criar conta"])
        with aba_login:
            _form_login()
        with aba_cadastro:
            _form_cadastro()
    with col_info:
        _painel_demo()


def _painel_demo() -> None:
    with st.container(border=True):
        st.markdown("#### Contas de demonstração")
        st.caption("Use estas contas para testar. Senha de todas: senha123")
        st.markdown(
            "- Administrador: `admin@ong.org`\n"
            "- Usuária: `maria@email.com`\n"
            "- Usuário: `joao@email.com`\n"
            "- Usuária: `ana@email.com`"
        )
        st.info("O administrador acessa o painel de gestão. Os demais são adotantes.")


def _form_login() -> None:
    with st.form("login"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        enviar = st.form_submit_button("Entrar", use_container_width=True)
    if enviar:
        try:
            with closing(get_connection()) as conn:
                usuario = servico_autenticacao.autenticar(conn, email, senha)
            session.iniciar_sessao(usuario)
            st.success(f"Bem-vindo(a), {usuario.nome}!")
            st.rerun()
        except ErroDominio as e:
            st.error(e.mensagem_usuario)


def _form_cadastro() -> None:
    with st.form("cadastro"):
        nome = st.text_input("Nome completo")
        email = st.text_input("Email ")
        senha = st.text_input("Senha ", type="password")
        nascimento = st.date_input(
            "Data de nascimento",
            min_value=date(1900, 1, 1), max_value=date.today(),
            value=date(2000, 1, 1),
        )
        codigo = st.text_input(
            "Código de acesso da ONG (opcional)",
            help="Deixe em branco para conta comum. Preencha apenas se a ONG forneceu um código de administrador.",
            type="password",
        )
        enviar = st.form_submit_button("Cadastrar", use_container_width=True)
    if enviar:
        faltando = campos_obrigatorios_ausentes(
            {"nome": nome, "email": email, "senha": senha},
            ["nome", "email", "senha"],
        )
        if faltando:
            st.error("Preencha: " + ", ".join(faltando))
            return
        try:
            with closing(get_connection()) as conn:
                usuario = servico_cadastro_usuario.cadastrar_usuario(
                    conn, nome, email, senha, nascimento.isoformat(),
                    codigo or None,
                )
            session.iniciar_sessao(usuario)
            st.success("Conta criada com sucesso!")
            st.rerun()
        except ErroDominio as e:
            st.error(e.mensagem_usuario)
