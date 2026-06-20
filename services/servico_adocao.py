"""Servico de adocao: solicitacao, listagem e decisao (aprovar/reprovar)."""
from __future__ import annotations

import json
import sqlite3

from repositories.animal_repository import AnimalRepository
from repositories.solicitacao_adocao_repository import SolicitacaoAdocaoRepository
from services import servico_auditoria
from services.errors import (
    AnimalIndisponivelError,
    CamposObrigatoriosError,
    SolicitacaoDuplicadaError,
)


def solicitar_adocao(conn, dono_id, animal_id, respostas_questionario: dict):
    # exige respostas do questionario (Req. 6.3)
    tem_resposta = False
    if respostas_questionario:
        for valor in respostas_questionario.values():
            if str(valor).strip():
                tem_resposta = True
                break
    if not tem_resposta:
        raise CamposObrigatoriosError("Responda o questionario de entrevista.")

    animal = AnimalRepository(conn).buscar_por_id(animal_id)
    if animal is None or animal["status"] != "disponivel":
        raise AnimalIndisponivelError()

    repo = SolicitacaoAdocaoRepository(conn)
    if repo.existe_em_analise(dono_id, animal_id):
        raise SolicitacaoDuplicadaError()

    return repo.inserir(dono_id, animal_id, respostas_questionario)


def listar_solicitacoes_do_dono(conn, dono_id):
    return SolicitacaoAdocaoRepository(conn).listar_por_dono(dono_id)


def listar_para_admin(conn, status=None):
    return SolicitacaoAdocaoRepository(conn).listar(status=status)


def aprovar_adocao(conn, solicitacao_id, admin_id, observacoes, aceite_termo):
    repo = SolicitacaoAdocaoRepository(conn)
    resultado = repo.aprovar_transacional(solicitacao_id, admin_id, observacoes, aceite_termo)
    servico_auditoria.registrar(
        conn, admin_id, "adocao_aprovada", "solicitacao_adocao",
        solicitacao_id, f"Animal {resultado['animal_id']} adotado",
    )
    return resultado


def reprovar_adocao(conn, solicitacao_id, admin_id, observacoes):
    repo = SolicitacaoAdocaoRepository(conn)
    repo.reprovar(solicitacao_id, admin_id, observacoes)
    servico_auditoria.registrar(
        conn, admin_id, "adocao_reprovada", "solicitacao_adocao",
        solicitacao_id, observacoes or "",
    )


def parse_respostas(raw: str) -> dict:
    """Desserializa o JSON de respostas do questionario."""
    try:
        return json.loads(raw) if raw else {}
    except (json.JSONDecodeError, TypeError):
        return {}
