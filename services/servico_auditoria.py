"""Servico de auditoria: registra e consulta eventos auditaveis."""
from __future__ import annotations

import sqlite3

from repositories.auditoria_repository import AuditoriaRepository


def registrar(conn: sqlite3.Connection, usuario_id, acao, entidade,
              registro_id=None, detalhe=None) -> None:
    AuditoriaRepository(conn).inserir(usuario_id, acao, entidade, registro_id, detalhe)


def listar_eventos(conn: sqlite3.Connection, limite: int = 200):
    return AuditoriaRepository(conn).listar(limite)
