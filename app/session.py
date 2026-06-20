"""Controle de sessao e RBAC sobre o st.session_state do Streamlit."""
from __future__ import annotations

import streamlit as st

from models.entities import Usuario
from services.errors import AcessoNegadoError

_CHAVE = "usuario_logado"


def iniciar_sessao(usuario: Usuario) -> None:
    st.session_state[_CHAVE] = usuario


def encerrar_sessao() -> None:
    st.session_state.pop(_CHAVE, None)


def usuario_atual() -> Usuario | None:
    return st.session_state.get(_CHAVE)


def autenticado() -> bool:
    return usuario_atual() is not None


def is_admin() -> bool:
    u = usuario_atual()
    return bool(u and u.is_admin)


def requer_autenticacao() -> Usuario:
    u = usuario_atual()
    if u is None:
        raise AcessoNegadoError("Faca login para continuar.")
    return u


def requer_admin() -> Usuario:
    u = requer_autenticacao()
    if not u.is_admin:
        raise AcessoNegadoError()
    return u
