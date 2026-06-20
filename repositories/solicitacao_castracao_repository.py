"""Acesso a dados de solicitacao_castracao (inclui agendamento). Parametrizado."""
from __future__ import annotations

import sqlite3


class SolicitacaoCastracaoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def inserir(self, usuario_id, nome_pet, especie, sexo, idade_pet,
                nome_tutor, telefone, endereco) -> int:
        cur = self._conn.execute(
            "INSERT INTO solicitacao_castracao (usuario_id, nome_pet, especie, sexo, "
            "idade_pet, nome_tutor, telefone, endereco) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (usuario_id, nome_pet, especie, sexo, idade_pet, nome_tutor, telefone, endereco),
        )
        self._conn.commit()
        return cur.lastrowid

    def listar_por_usuario(self, usuario_id: int) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM solicitacao_castracao WHERE usuario_id=? "
            "ORDER BY data_solicitacao DESC",
            (usuario_id,),
        ).fetchall()

    def listar(self, status: str | None = None) -> list[sqlite3.Row]:
        sql = (
            "SELECT sc.*, u.nome AS nome_usuario FROM solicitacao_castracao sc "
            "JOIN usuario u ON u.id = sc.usuario_id"
        )
        params: tuple = ()
        if status:
            sql += " WHERE sc.status = ?"
            params = (status,)
        sql += " ORDER BY (sc.data_agendada IS NULL), sc.data_agendada, sc.data_solicitacao DESC"
        return self._conn.execute(sql, params).fetchall()

    def listar_agenda(self) -> list[sqlite3.Row]:
        """Castracoes aprovadas e agendadas, ordenadas por data do procedimento."""
        return self._conn.execute(
            "SELECT sc.*, u.nome AS nome_usuario FROM solicitacao_castracao sc "
            "JOIN usuario u ON u.id = sc.usuario_id "
            "WHERE sc.status='aprovado' AND sc.data_agendada IS NOT NULL "
            "ORDER BY sc.data_agendada"
        ).fetchall()

    def atualizar_status(self, solicitacao_id, admin_id, status, data_agendada=None) -> None:
        self._conn.execute(
            "UPDATE solicitacao_castracao "
            "SET status=?, data_agendada=?, decidido_por=?, decidido_em=datetime('now') "
            "WHERE id=?",
            (status, data_agendada, admin_id, solicitacao_id),
        )
        self._conn.commit()
