"""Leitura centralizada de configuracao a partir de variaveis de ambiente.

Nenhum valor sensivel e hardcoded. As variaveis sao lidas do arquivo .env
(via python-dotenv) ou do ambiente do sistema.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Raiz do projeto (pasta que contem este arquivo app/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega o .env da raiz do projeto, se existir
load_dotenv(BASE_DIR / ".env")


def _abs(path_str: str) -> Path:
    """Resolve um caminho relativo a partir da raiz do projeto."""
    p = Path(path_str)
    return p if p.is_absolute() else (BASE_DIR / p)


# Caminho do arquivo de banco SQLite
DB_PATH: Path = _abs(os.getenv("DB_PATH", "./ong_adocao.db"))

# Codigo de acesso que concede perfil de administrador no cadastro
CODIGO_ACESSO_ONG: str = os.getenv("CODIGO_ACESSO_ONG", "0000")

# Diretorio raiz para arquivos enviados (fotos/documentos)
STORAGE_DIR: Path = _abs(os.getenv("STORAGE_DIR", "./storage"))

# Caminho do schema SQL (usado para inicializar o banco)
SCHEMA_PATH: Path = BASE_DIR / "db" / "schema.sql"
SEED_PATH: Path = BASE_DIR / "db" / "seed.sql"
