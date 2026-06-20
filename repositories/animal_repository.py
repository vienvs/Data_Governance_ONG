"""Acesso a dados da entidade animal. Queries parametrizadas."""
from __future__ import annotations

import sqlite3


class AnimalRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def inserir(self, nome, especie, sexo, idade, raca, descricao, caminho_foto) -> int:
        cur = self._conn.execute(
            "INSERT INTO animal (nome, especie, sexo, idade, raca, descricao, caminho_foto) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nome, especie, sexo, idade, raca, descricao, caminho_foto),
        )
        self._conn.commit()
        return cur.lastrowid

    def atualizar(self, animal_id, nome, especie, sexo, idade, raca, descricao) -> None:
        self._conn.execute(
            "UPDATE animal SET nome=?, especie=?, sexo=?, idade=?, raca=?, descricao=? "
            "WHERE id=?",
            (nome, especie, sexo, idade, raca, descricao, animal_id),
        )
        self._conn.commit()

    def remover(self, animal_id: int) -> None:
        self._conn.execute("DELETE FROM animal WHERE id=?", (animal_id,))
        self._conn.commit()

    def buscar_por_id(self, animal_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT * FROM animal WHERE id = ?", (animal_id,)
        ).fetchone()

    def listar_disponiveis(self) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT * FROM animal WHERE status = 'disponivel' ORDER BY nome"
        ).fetchall()

    def listar(self, status: str | None = None, especie: str | None = None) -> list[sqlite3.Row]:
        sql = "SELECT * FROM animal"
        cond = []
        params: list = []
        if status:
            cond.append("status = ?")
            params.append(status)
        if especie:
            cond.append("especie = ?")
            params.append(especie)
        if cond:
            sql += " WHERE " + " AND ".join(cond)
        sql += " ORDER BY nome"
        return self._conn.execute(sql, tuple(params)).fetchall()
