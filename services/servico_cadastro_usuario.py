"""Servico de cadastro de usuarios (comum/admin via codigo de acesso)."""
from __future__ import annotations

import sqlite3

from app import config
from models.entities import TipoUsuario, Usuario
from repositories.usuario_repository import UsuarioRepository
from services.errors import (
    CodigoAcessoInvalidoError,
    EmailInvalidoError,
    EmailJaExistenteError,
)
from services.servico_autenticacao import gerar_hash_senha
from services.validators import validar_email


def _resolver_tipo(codigo_acesso: str | None) -> str:
    """None/vazio -> comum; igual ao codigo da ONG -> admin; diferente -> erro."""
    if not codigo_acesso:
        return TipoUsuario.COMUM.value
    if codigo_acesso == config.CODIGO_ACESSO_ONG:
        return TipoUsuario.ADMIN.value
    raise CodigoAcessoInvalidoError()


def cadastrar_usuario(conn: sqlite3.Connection, nome: str, email: str, senha: str,
                      data_nascimento: str, codigo_acesso: str | None = None) -> Usuario:
    email = (email or "").strip().lower()
    if not validar_email(email):
        raise EmailInvalidoError()

    tipo = _resolver_tipo(codigo_acesso.strip() if codigo_acesso else None)

    repo = UsuarioRepository(conn)
    if repo.existe_email(email):
        raise EmailJaExistenteError()

    senha_hash = gerar_hash_senha(senha)
    novo_id = repo.inserir(nome.strip(), email, senha_hash, data_nascimento, tipo)
    return Usuario(
        id=novo_id, nome=nome.strip(), email=email, senha_hash=senha_hash,
        data_nascimento=data_nascimento, tipo=tipo,
    )
