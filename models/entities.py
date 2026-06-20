"""Entidades de dominio e enums.

Os valores dos enums correspondem exatamente aos rotulos aceitos pelas
restricoes CHECK do schema (db/schema.sql).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class TipoUsuario(str, Enum):
    COMUM = "comum"
    ADMIN = "admin"


class StatusAprovacao(str, Enum):
    EM_ANALISE = "em_analise"
    APROVADO = "aprovado"
    REPROVADO = "reprovado"


class StatusAnimal(str, Enum):
    DISPONIVEL = "disponivel"
    ADOTADO = "adotado"


class Especie(str, Enum):
    CAO = "cao"
    GATO = "gato"


class Sexo(str, Enum):
    MACHO = "macho"
    FEMEA = "femea"


class TipoResidencia(str, Enum):
    CASA = "casa"
    APARTAMENTO = "apartamento"


# Rotulos amigaveis para exibicao na interface
ROTULOS = {
    "tipo_usuario": {"comum": "Usuário comum", "admin": "Administrador"},
    "status_aprovacao": {
        "em_analise": "Em análise",
        "aprovado": "Aprovado",
        "reprovado": "Reprovado",
    },
    "status_animal": {"disponivel": "Disponível", "adotado": "Adotado"},
    "especie": {"cao": "Cão", "gato": "Gato"},
    "sexo": {"macho": "Macho", "femea": "Fêmea"},
    "tipo_residencia": {"casa": "Casa", "apartamento": "Apartamento"},
}


def rotulo(dominio: str, valor: str) -> str:
    """Traduz um valor de dominio para exibicao amigavel."""
    return ROTULOS.get(dominio, {}).get(valor, valor)


@dataclass
class Usuario:
    id: int | None
    nome: str
    email: str
    senha_hash: str
    data_nascimento: str
    tipo: str = TipoUsuario.COMUM.value
    criado_em: str | None = None

    @property
    def is_admin(self) -> bool:
        return self.tipo == TipoUsuario.ADMIN.value


@dataclass
class Dono:
    id: int | None
    usuario_id: int
    cpf: str
    telefone: str
    endereco: str
    tipo_residencia: str
    tem_tela: bool
    caminho_doc: str
    caminho_comprovante: str
    caminho_tela: str
    status_aprovacao: str = StatusAprovacao.EM_ANALISE.value
    criado_em: str | None = None


@dataclass
class Animal:
    id: int | None
    nome: str
    especie: str
    sexo: str
    idade: int
    raca: str | None = None
    descricao: str | None = None
    status: str = StatusAnimal.DISPONIVEL.value
    caminho_foto: str | None = None
    criado_em: str | None = None


@dataclass
class SolicitacaoAdocao:
    id: int | None
    dono_id: int
    animal_id: int
    respostas_questionario: dict
    data_solicitacao: str | None = None
    status: str = StatusAprovacao.EM_ANALISE.value
    observacoes_admin: str | None = None
    aceite_termo: bool = False
    decidido_por: int | None = None
    decidido_em: str | None = None


@dataclass
class SolicitacaoCastracao:
    id: int | None
    usuario_id: int
    nome_pet: str
    especie: str
    sexo: str
    idade_pet: int
    nome_tutor: str
    telefone: str
    endereco: str
    data_solicitacao: str | None = None
    data_agendada: str | None = None
    status: str = StatusAprovacao.EM_ANALISE.value
    decidido_por: int | None = None
    decidido_em: str | None = None


@dataclass
class LogAuditoria:
    id: int | None
    usuario_id: int | None
    acao: str
    entidade: str
    registro_id: int | None = None
    detalhe: str | None = None
    data_hora: str | None = None
