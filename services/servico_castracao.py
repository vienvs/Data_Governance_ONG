"""Servico de castracao: registro, listagem, decisao e agendamento."""
from __future__ import annotations

import sqlite3

from repositories.solicitacao_castracao_repository import SolicitacaoCastracaoRepository
from services import servico_auditoria


def solicitar_castracao(conn, usuario_id, nome_pet, especie, sexo, idade_pet,
                        nome_tutor, telefone, endereco):
    repo = SolicitacaoCastracaoRepository(conn)
    novo_id = repo.inserir(usuario_id, nome_pet, especie, sexo, int(idade_pet),
                           nome_tutor, telefone, endereco)
    return novo_id


def listar_do_usuario(conn, usuario_id):
    return SolicitacaoCastracaoRepository(conn).listar_por_usuario(usuario_id)


def listar_para_admin(conn, status=None):
    return SolicitacaoCastracaoRepository(conn).listar(status=status)


def listar_agenda(conn):
    return SolicitacaoCastracaoRepository(conn).listar_agenda()


def atualizar_status_castracao(conn, solicitacao_id, admin_id, novo_status, data_agendada=None):
    repo = SolicitacaoCastracaoRepository(conn)
    repo.atualizar_status(solicitacao_id, admin_id, novo_status, data_agendada)
    servico_auditoria.registrar(
        conn, admin_id, f"castracao_{novo_status}", "solicitacao_castracao",
        solicitacao_id, f"Status alterado para {novo_status}"
        + (f"; agendada para {data_agendada}" if data_agendada else ""),
    )
