"""Servico de animais: cadastro/edicao (admin), upload de foto, listagens."""
from __future__ import annotations

import sqlite3

from repositories.animal_repository import AnimalRepository
from services import file_storage


def cadastrar_animal(conn, nome, especie, sexo, idade, raca, descricao, foto=None):
    if int(idade) < 0:
        raise ValueError("A idade deve ser maior ou igual a zero.")
    caminho_foto = None
    if foto is not None:
        caminho_foto = file_storage.salvar_arquivo(foto, "animais")
    repo = AnimalRepository(conn)
    animal_id = repo.inserir(nome, especie, sexo, int(idade), raca, descricao, caminho_foto)
    return repo.buscar_por_id(animal_id)


def editar_animal(conn, animal_id, nome, especie, sexo, idade, raca, descricao):
    repo = AnimalRepository(conn)
    repo.atualizar(animal_id, nome, especie, sexo, int(idade), raca, descricao)
    return repo.buscar_por_id(animal_id)


def remover_animal(conn, animal_id):
    AnimalRepository(conn).remover(animal_id)


def listar_disponiveis(conn: sqlite3.Connection):
    return AnimalRepository(conn).listar_disponiveis()


def listar_para_admin(conn, status=None, especie=None):
    return AnimalRepository(conn).listar(status=status, especie=especie)
