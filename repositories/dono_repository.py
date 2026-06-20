"""Acesso a dados da entidade dono. Queries parametrizadas."""
from __future__ import annotations

import sqlite3


class DonoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def inserir(self, usuario_id, cpf, telefone, endereco, tipo_residencia,
                tem_tela, caminho_doc, caminho_comprovante, caminho_tela) -> int:
        cur = self._conn.execute(
            "INSERT INTO dono (usuario_id, cpf, telefone, endereco, tipo_residencia, "
            "tem_tela, caminho_doc, caminho_comprovante, caminho_tela) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (usuario_id, cpf, telefone, endereco, tipo_residencia,
             1 if tem_tela else 0, caminho_doc, caminho_comprovante, caminho_tela),
        )
        self._conn.commit()
        return cur.lastrowid

    def buscar_por_usuario(self, usuario_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT * FROM dono WHERE usuario_id = ?", (usuario_id,)
        ).fetchone()

    def buscar_por_id(self, dono_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT * FROM dono WHERE id = ?", (dono_id,)
        ).fetchone()

    def existe_cpf(self, cpf: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM dono WHERE cpf = ? LIMIT 1", (cpf,)
        ).fetchone()
        return row is not None

    def atualizar(self, dono_id, telefone, endereco, tipo_residencia, tem_tela) -> None:
        self._conn.execute(
            "UPDATE dono SET telefone=?, endereco=?, tipo_residencia=?, tem_tela=? "
            "WHERE id=?",
            (telefone, endereco, tipo_residencia, 1 if tem_tela else 0, dono_id),
        )
        self._conn.commit()

    def atualizar_status(self, dono_id, status) -> None:
        self._conn.execute(
            "UPDATE dono SET status_aprovacao=? WHERE id=?", (status, dono_id)
        )
        self._conn.commit()

    def listar(self, status: str | None = None) -> list[sqlite3.Row]:
        sql = (
            "SELECT d.*, u.nome AS nome_usuario, u.email AS email_usuario "
            "FROM dono d JOIN usuario u ON u.id = d.usuario_id"
        )
        params: tuple = ()
        if status:
            sql += " WHERE d.status_aprovacao = ?"
            params = (status,)
        sql += " ORDER BY d.criado_em DESC"
        return self._conn.execute(sql, params).fetchall()
