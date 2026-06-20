"""Acesso a dados do log de auditoria. Parametrizado."""
from __future__ import annotations

import sqlite3


class AuditoriaRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def inserir(self, usuario_id, acao, entidade, registro_id=None, detalhe=None) -> int:
        cur = self._conn.execute(
            "INSERT INTO log_auditoria (usuario_id, acao, entidade, registro_id, detalhe) "
            "VALUES (?, ?, ?, ?, ?)",
            (usuario_id, acao, entidade, registro_id, detalhe),
        )
        self._conn.commit()
        return cur.lastrowid

    def listar(self, limite: int = 200) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT la.*, u.nome AS nome_usuario FROM log_auditoria la "
            "LEFT JOIN usuario u ON u.id = la.usuario_id "
            "ORDER BY la.data_hora DESC LIMIT ?",
            (limite,),
        ).fetchall()
