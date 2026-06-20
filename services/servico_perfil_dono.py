"""Servico de perfil de Dono: cadastro/complemento, validacao de CPF, uploads."""
from __future__ import annotations

import sqlite3

from repositories.dono_repository import DonoRepository
from services import file_storage
from services.errors import (
    CpfInvalidoError,
    CpfJaExistenteError,
    PerfilDonoJaExisteError,
)
from services.validators import normalizar_cpf, validar_cpf


def obter_perfil_por_usuario(conn: sqlite3.Connection, usuario_id: int):
    return DonoRepository(conn).buscar_por_usuario(usuario_id)


def criar_perfil_dono(conn, usuario_id, cpf, telefone, endereco, tipo_residencia,
                      tem_tela, doc_identificacao, comprovante_residencia, foto_tela):
    repo = DonoRepository(conn)

    if not validar_cpf(cpf):
        raise CpfInvalidoError()
    cpf_norm = normalizar_cpf(cpf)

    if repo.buscar_por_usuario(usuario_id) is not None:
        raise PerfilDonoJaExisteError()
    if repo.existe_cpf(cpf_norm):
        raise CpfJaExistenteError()

    # grava os arquivos no filesystem e obtem os caminhos relativos
    caminho_doc = file_storage.salvar_arquivo(doc_identificacao, "documentos")
    caminho_comp = file_storage.salvar_arquivo(comprovante_residencia, "comprovantes")
    caminho_tela = file_storage.salvar_arquivo(foto_tela, "telas")

    dono_id = repo.inserir(
        usuario_id, cpf_norm, telefone, endereco, tipo_residencia,
        tem_tela, caminho_doc, caminho_comp, caminho_tela,
    )
    return repo.buscar_por_id(dono_id)


def atualizar_perfil_dono(conn, dono_id, telefone, endereco, tipo_residencia, tem_tela):
    repo = DonoRepository(conn)
    dono = repo.buscar_por_id(dono_id)
    if dono is not None and dono["status_aprovacao"] == "em_analise":
        repo.atualizar(dono_id, telefone, endereco, tipo_residencia, tem_tela)
    return repo.buscar_por_id(dono_id)
