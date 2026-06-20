"""Validadores puros (sem efeitos colaterais).

Sao alvos ideais de testes baseados em propriedades (Hypothesis).
"""
from __future__ import annotations

import re
from datetime import date

EXTENSOES_IMAGEM_PERMITIDAS = {".jpg", ".jpeg", ".png", ".webp"}

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_email(email: str) -> bool:
    """Retorna True se a string for um email bem formado."""
    if not isinstance(email, str):
        return False
    return bool(_EMAIL_RE.match(email.strip()))


def normalizar_cpf(cpf: str) -> str:
    """Remove qualquer caractere que nao seja digito. Idempotente."""
    if not isinstance(cpf, str):
        return ""
    return re.sub(r"\D", "", cpf)


def validar_cpf(cpf: str) -> bool:
    """Retorna True se o valor normalizado tiver exatamente 11 digitos."""
    normalizado = normalizar_cpf(cpf)
    return len(normalizado) == 11 and normalizado.isdigit()


def is_maior_de_idade(data_nascimento: date, hoje: date) -> bool:
    """True se a idade completa em anos for >= 18 na data de referencia."""
    idade = hoje.year - data_nascimento.year - (
        (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day)
    )
    return idade >= 18


def extensao_imagem_permitida(nome_arquivo: str) -> bool:
    """True se a extensao (case-insensitive) estiver no conjunto permitido."""
    if not isinstance(nome_arquivo, str) or "." not in nome_arquivo:
        return False
    ext = "." + nome_arquivo.rsplit(".", 1)[1].lower()
    return ext in EXTENSOES_IMAGEM_PERMITIDAS


def campos_obrigatorios_ausentes(payload: dict, obrigatorios: list[str]) -> list[str]:
    """Retorna o conjunto exato de campos obrigatorios ausentes ou vazios."""
    ausentes = []
    for campo in obrigatorios:
        valor = payload.get(campo)
        if valor is None or (isinstance(valor, str) and valor.strip() == ""):
            ausentes.append(campo)
    return ausentes
