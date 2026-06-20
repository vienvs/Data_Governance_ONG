"""Gravacao e leitura de arquivos enviados no filesystem local.

Apenas o caminho relativo e persistido no banco; o arquivo fica em
storage/<categoria>/. Valida a extensao antes de gravar.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from app import config
from services.errors import ArquivoInvalidoError
from services.validators import extensao_imagem_permitida

CATEGORIAS = {"documentos", "comprovantes", "telas", "animais"}


def _garantir_diretorio(categoria: str) -> Path:
    destino = config.STORAGE_DIR / categoria
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def salvar_arquivo(arquivo, categoria: str, chave: str = "") -> str:
    """Valida a extensao, gera um nome unico e grava o arquivo.

    `arquivo` deve ter atributos `.name` e `.getbuffer()`/`.read()`
    (compativel com o UploadedFile do Streamlit).
    Retorna o caminho RELATIVO (ex.: "documentos/ab12.jpg") para persistir.
    """
    nome_original = getattr(arquivo, "name", "")
    if not extensao_imagem_permitida(nome_original):
        raise ArquivoInvalidoError()

    ext = "." + nome_original.rsplit(".", 1)[1].lower()
    nome_unico = f"{chave + '_' if chave else ''}{uuid.uuid4().hex}{ext}"

    destino_dir = _garantir_diretorio(categoria)
    destino = destino_dir / nome_unico

    dados = arquivo.getbuffer() if hasattr(arquivo, "getbuffer") else arquivo.read()
    with open(destino, "wb") as f:
        f.write(dados)

    return f"{categoria}/{nome_unico}"


def caminho_absoluto(caminho_relativo: str) -> Path:
    """Resolve o caminho absoluto a partir do caminho relativo persistido."""
    return config.STORAGE_DIR / caminho_relativo


def arquivo_existe(caminho_relativo: str | None) -> bool:
    """True se o arquivo referenciado existir no filesystem."""
    if not caminho_relativo:
        return False
    return caminho_absoluto(caminho_relativo).is_file()
