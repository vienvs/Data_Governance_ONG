"""Cadastro/complemento do perfil de Dono (adotante)."""
from __future__ import annotations

from contextlib import closing

import streamlit as st

from app import session
from db.connection import get_connection
from models.entities import rotulo
from services import servico_perfil_dono
from services.errors import ErroDominio
from services.validators import campos_obrigatorios_ausentes


def render() -> None:
    usuario = session.requer_autenticacao()
    st.title("Meu perfil de adotante")

    with closing(get_connection()) as conn:
        perfil = servico_perfil_dono.obter_perfil_por_usuario(conn, usuario.id)

    if perfil is not None:
        _mostrar_perfil(perfil)
        return

    st.info(
        "Para solicitar uma adocao, complete seu perfil com seus dados e documentos. "
        "Apos o envio, a ONG fara a verificacao manual dos documentos."
    )
    _form_criar(usuario)


def _mostrar_perfil(perfil) -> None:
    st.success(
        f"Perfil enviado. Status: **{rotulo('status_aprovacao', perfil['status_aprovacao'])}**"
    )
    st.write(
        f"**CPF:** {perfil['cpf']}  \n"
        f"**Telefone:** {perfil['telefone']}  \n"
        f"**Endereco:** {perfil['endereco']}  \n"
        f"**Residencia:** {rotulo('tipo_residencia', perfil['tipo_residencia'])} "
        f"({'telada' if perfil['tem_tela'] else 'sem tela'})"
    )
    if perfil["status_aprovacao"] == "em_analise":
        st.caption("Seu cadastro esta em analise pela administracao da ONG.")


def _form_criar(usuario) -> None:
    with st.form("perfil_dono"):
        cpf = st.text_input("CPF (somente numeros)")
        telefone = st.text_input("Telefone")
        endereco = st.text_input("Endereco completo")
        tipo_residencia = st.selectbox("Tipo de residencia", ["casa", "apartamento"],
                                       format_func=lambda v: rotulo("tipo_residencia", v))
        tem_tela = st.checkbox("Minha residencia e telada, sem acesso a rua")
        st.markdown("**Documentos (imagens JPG/PNG/WEBP):**")
        doc = st.file_uploader("Documento de identificacao", type=["jpg", "jpeg", "png", "webp"])
        comp = st.file_uploader("Comprovante de residencia", type=["jpg", "jpeg", "png", "webp"])
        tela = st.file_uploader("Foto da tela/protecao da residencia", type=["jpg", "jpeg", "png", "webp"])
        enviar = st.form_submit_button("Enviar perfil")

    if enviar:
        faltando = campos_obrigatorios_ausentes(
            {"cpf": cpf, "telefone": telefone, "endereco": endereco},
            ["cpf", "telefone", "endereco"],
        )
        if faltando:
            st.error("Preencha: " + ", ".join(faltando))
            return
        if not (doc and comp and tela):
            st.error("Envie as tres imagens (documento, comprovante e tela).")
            return
        try:
            with closing(get_connection()) as conn:
                servico_perfil_dono.criar_perfil_dono(
                    conn, usuario.id, cpf, telefone, endereco, tipo_residencia,
                    tem_tela, doc, comp, tela,
                )
            st.success("Perfil enviado para analise!")
            st.rerun()
        except ErroDominio as e:
            st.error(e.mensagem_usuario)
