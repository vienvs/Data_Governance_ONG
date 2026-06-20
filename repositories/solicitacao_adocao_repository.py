"""Acesso a dados de solicitacao_adocao, incluindo a aprovacao transacional.

A aprovacao e atomica: implementada em Python com transacao sqlite3
(BEGIN/COMMIT/ROLLBACK). O indice unico parcial uq_uma_adocao_aprovada_por_animal
e a defesa final contra concorrencia: sua violacao vira AnimalJaAdotadoError.
"""
from __future__ import annotations

import json
import sqlite3

from services.errors import (
    AceiteTermoObrigatorioError,
    AnimalJaAdotadoError,
    SolicitacaoInexistenteError,
)


class SolicitacaoAdocaoRepository:
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def inserir(self, dono_id, animal_id, respostas_questionario: dict) -> int:
        cur = self._conn.execute(
            "INSERT INTO solicitacao_adocao (dono_id, animal_id, respostas_questionario) "
            "VALUES (?, ?, ?)",
            (dono_id, animal_id, json.dumps(respostas_questionario, ensure_ascii=False)),
        )
        self._conn.commit()
        return cur.lastrowid

    def existe_em_analise(self, dono_id, animal_id) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM solicitacao_adocao "
            "WHERE dono_id=? AND animal_id=? AND status='em_analise' LIMIT 1",
            (dono_id, animal_id),
        ).fetchone()
        return row is not None

    def buscar_por_id(self, solicitacao_id: int) -> sqlite3.Row | None:
        return self._conn.execute(
            "SELECT * FROM solicitacao_adocao WHERE id=?", (solicitacao_id,)
        ).fetchone()

    def listar_por_dono(self, dono_id: int) -> list[sqlite3.Row]:
        return self._conn.execute(
            "SELECT sa.*, a.nome AS nome_animal, a.especie AS especie_animal "
            "FROM solicitacao_adocao sa JOIN animal a ON a.id = sa.animal_id "
            "WHERE sa.dono_id=? ORDER BY sa.data_solicitacao DESC",
            (dono_id,),
        ).fetchall()

    def listar(self, status: str | None = None) -> list[sqlite3.Row]:
        sql = (
            "SELECT sa.*, a.nome AS nome_animal, u.nome AS nome_adotante "
            "FROM solicitacao_adocao sa "
            "JOIN animal a ON a.id = sa.animal_id "
            "JOIN dono d ON d.id = sa.dono_id "
            "JOIN usuario u ON u.id = d.usuario_id"
        )
        params: tuple = ()
        if status:
            sql += " WHERE sa.status = ?"
            params = (status,)
        sql += " ORDER BY sa.data_solicitacao DESC"
        return self._conn.execute(sql, params).fetchall()

    def reprovar(self, solicitacao_id, admin_id, observacoes) -> None:
        self._conn.execute(
            "UPDATE solicitacao_adocao "
            "SET status='reprovado', observacoes_admin=?, decidido_por=?, "
            "decidido_em=datetime('now') WHERE id=? AND status='em_analise'",
            (observacoes, admin_id, solicitacao_id),
        )
        self._conn.commit()

    def aprovar_transacional(self, solicitacao_id, admin_id, observacoes, aceite_termo) -> dict:
        """Aprovacao atomica (tudo ou nada).

        1) valida aceite do termo
        2) localiza a solicitacao em analise e o animal
        3) checa disponibilidade do animal
        4) aprova a solicitacao + grava aceite do termo
        5) marca o animal como adotado
        6) reprova as demais solicitacoes em analise do mesmo animal
        """
        if not aceite_termo:
            raise AceiteTermoObrigatorioError()

        conn = self._conn
        try:
            conn.execute("BEGIN")

            row = conn.execute(
                "SELECT animal_id FROM solicitacao_adocao "
                "WHERE id=? AND status='em_analise'",
                (solicitacao_id,),
            ).fetchone()
            if row is None:
                raise SolicitacaoInexistenteError()
            animal_id = row["animal_id"]

            animal = conn.execute(
                "SELECT status FROM animal WHERE id=?", (animal_id,)
            ).fetchone()
            if animal is None or animal["status"] == "adotado":
                raise AnimalJaAdotadoError()

            conn.execute(
                "UPDATE solicitacao_adocao "
                "SET status='aprovado', observacoes_admin=?, aceite_termo=1, "
                "decidido_por=?, decidido_em=datetime('now') WHERE id=?",
                (observacoes, admin_id, solicitacao_id),
            )
            conn.execute(
                "UPDATE animal SET status='adotado' WHERE id=?", (animal_id,)
            )
            conn.execute(
                "UPDATE solicitacao_adocao "
                "SET status='reprovado', decidido_por=?, decidido_em=datetime('now') "
                "WHERE animal_id=? AND id<>? AND status='em_analise'",
                (admin_id, animal_id, solicitacao_id),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            # violacao do indice unico parcial: outra aprovacao ja marcou este animal
            conn.rollback()
            raise AnimalJaAdotadoError()
        except Exception:
            conn.rollback()
            raise

        return {"solicitacao_id": solicitacao_id, "animal_id": animal_id}
