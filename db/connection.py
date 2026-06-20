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


def carregar_seed(
    db_path: str | Path | None = None,
    seed_path: str | Path | None = None,
) -> None:
    """Executa o seed.sql (dados de teste) no banco informado."""
    seed = Path(seed_path or config.SEED_PATH)
    sql = seed.read_text(encoding="utf-8")
    conn = get_connection(db_path)
    try:
        conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


def garantir_dados_iniciais(db_path: str | Path | None = None) -> None:
    """Carrega o seed apenas se o banco estiver vazio (nenhum usuario).

    Util para deploys efemeros (ex.: Streamlit Cloud), onde o banco e
    recriado a cada inicializacao. Nao apaga dados existentes.
    """
    conn = get_connection(db_path)
    try:
        vazio = conn.execute("SELECT COUNT(*) FROM usuario").fetchone()[0] == 0
    finally:
        conn.close()
    if vazio:
        carregar_seed(db_path)
