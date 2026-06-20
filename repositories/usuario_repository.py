"""Acesso a dados da entidade usuario. Todas as queries sao parametrizadas."""
from __future__ import annotations

import sqlite3


class UsuarioRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def inserir(self, nome, email, senha_hash, data_nascimento, tipo) -> int:
        cur = self._conn.execute(
            "INSERT INTO usuario (nome, email, senha_hash, data_nascimento, tipo) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, email, senha_hash, data_nascimento, tipo),
        )
        self._conn.commit()
        return cur.lastrowid

    def buscar_por_email(self, email: str) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT * FROM usuario WHERE email = ?", (email,)
        ).fetchone()

    def buscar_por_id(self, usuario_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT * FROM usuario WHERE id = ?", (usuario_id,)
        ).fetchone()

    def existe_email(self, email: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM usuario WHERE email = ? LIMIT 1", (email,)
        ).fetchone()
        return row is not None

    def listar(self) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM usuario ORDER BY criado_em DESC"
        ).fetchall()
