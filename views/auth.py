"""Telas de autenticacao: login e cadastro."""
from __future__ import annotations

from contextlib import closing
from datetime import date

import streamlit as st

from app import session
from db.connection import get_connection
from services import servico_autenticacao, servico_cadastro_usuario
from services.errors import ErroDominio
from services.validators import campos_obrigatorios_ausentes


def render() -> None:
    st.title("ONG de Adocao - Acesso")
    aba_login, aba_cadastro = st.tabs(["Entrar", "Criar conta"])

    with aba_login:
        _form_login()
    with aba_cadastro:
        _form_cadastro()


def _form_login() -> None:
    with st.form("login"):
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")
        enviar = st.form_submit_button("Entrar")
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
            "Codigo de acesso da ONG (opcional)",
            help="Deixe em branco para conta comum. Preencha apenas se a ONG forneceu um codigo de administrador.",
            type="password",
        )
        enviar = st.form_submit_button("Cadastrar")
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
