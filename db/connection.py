"""Gerenciamento de conexoes SQLite com integridade e transacoes.

- Ativa PRAGMA foreign_keys = ON em toda conexao (o SQLite nao aplica FKs
  por padrao).
- Define row_factory = sqlite3.Row para acesso por nome de coluna.
- Fornece um context manager de transacao (commit no sucesso, rollback em erro).
- Permite inicializar o banco a partir do schema.sql.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app import config


def get_connection(db_path: str | Path | None = None) -> sqlite3.Connection:
    """Abre uma conexao SQLite configurada.

    Ativa chaves estrangeiras e define o row_factory para dicionarios.
    """
    caminho = str(db_path or config.DB_PATH)
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def transacao(conn: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Executa um bloco em uma transacao: commit no sucesso, rollback em excecao."""
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def inicializar_banco(
    db_path: str | Path | None = None,
    schema_path: str | Path | None = None,
) -> None:
    """Cria as tabelas/indices/views a partir do schema.sql (idempotente)."""
    schema = Path(schema_path or config.SCHEMA_PATH)
    sql = schema.read_text(encoding="utf-8")
    conn = get_connection(db_path)
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()
