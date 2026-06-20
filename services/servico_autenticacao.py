"""Servico de autenticacao: hash de senha e verificacao de credenciais."""
from __future__ import annotations

import sqlite3

import bcrypt

from models.entities import Usuario
from repositories.usuario_repository import UsuarioRepository
from services import servico_auditoria
from services.errors import CredenciaisInvalidasError

# bcrypt limita a senha a 72 bytes; truncamos com seguranca antes de processar.
_LIMITE_BYTES = 72


def _to_bytes(senha: str) -> bytes:
    return (senha or "").encode("utf-8")[:_LIMITE_BYTES]


def gerar_hash_senha(senha: str) -> str:
    """Gera hash bcrypt com salt embutido."""
    return bcrypt.hashpw(_to_bytes(senha), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha_informada: str, hash_armazenado: str) -> bool:
    """Compara a senha informada com o hash armazenado."""
    try:
        return bcrypt.checkpw(_to_bytes(senha_informada), hash_armazenado.encode("utf-8"))
    except Exception:
        return False


def _row_para_usuario(row) -> Usuario:
    return Usuario(
        id=row["id"], nome=row["nome"], email=row["email"],
        senha_hash=row["senha_hash"], data_nascimento=row["data_nascimento"],
        tipo=row["tipo"], criado_em=row["criado_em"],
    )


def autenticar(conn: sqlite3.Connection, email: str, senha: str) -> Usuario:
    """Valida credenciais e retorna o Usuario. Registra o login na auditoria."""
    repo = UsuarioRepository(conn)
    row = repo.buscar_por_email((email or "").strip().lower())
    if row is None or not verificar_senha(senha, row["senha_hash"]):
        raise CredenciaisInvalidasError()
    usuario = _row_para_usuario(row)
    servico_auditoria.registrar(
        conn, usuario.id, "login", "usuario", usuario.id, "Autenticacao bem-sucedida"
    )
    return usuario
