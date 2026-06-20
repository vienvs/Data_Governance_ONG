"""Hierarquia de excecoes de dominio.

Os servicos lancam estas excecoes; a camada de apresentacao (Streamlit)
captura ErroDominio e exibe a mensagem amigavel ao usuario.
"""
from __future__ import annotations


class ErroDominio(Exception):
    """Base de todas as excecoes de regra de negocio."""

    mensagem_usuario: str = "Ocorreu um erro ao processar a solicitacao."

    def __init__(self, mensagem: str | None = None):
        super().__init__(mensagem or self.mensagem_usuario)
        self.mensagem_usuario = mensagem or self.mensagem_usuario


# Autenticacao e cadastro
class CredenciaisInvalidasError(ErroDominio):
    mensagem_usuario = "Email ou senha invalidos."


class CodigoAcessoInvalidoError(ErroDominio):
    mensagem_usuario = "Codigo de acesso da ONG invalido."


class EmailJaExistenteError(ErroDominio):
    mensagem_usuario = "Ja existe uma conta com este email."


class EmailInvalidoError(ErroDominio):
    mensagem_usuario = "O email informado nao tem um formato valido."


# Perfil de Dono
class CpfInvalidoError(ErroDominio):
    mensagem_usuario = "O CPF deve conter 11 digitos numericos."


class CpfJaExistenteError(ErroDominio):
    mensagem_usuario = "Este CPF ja esta cadastrado."


class PerfilDonoJaExisteError(ErroDominio):
    mensagem_usuario = "Voce ja possui um perfil de dono."


# Adocao
class AnimalIndisponivelError(ErroDominio):
    mensagem_usuario = "Este animal nao esta disponivel para adocao."


class AnimalJaAdotadoError(ErroDominio):
    mensagem_usuario = "Este animal ja foi adotado."


class SolicitacaoDuplicadaError(ErroDominio):
    mensagem_usuario = "Voce ja possui uma solicitacao em analise para este animal."


class AceiteTermoObrigatorioError(ErroDominio):
    mensagem_usuario = "E necessario aceitar o Termo de Compromisso para concluir a adocao."


class SolicitacaoInexistenteError(ErroDominio):
    mensagem_usuario = "Solicitacao inexistente ou nao esta em analise."


# Acesso e arquivos
class AcessoNegadoError(ErroDominio):
    mensagem_usuario = "Voce nao tem permissao para executar esta operacao."


class ArquivoInvalidoError(ErroDominio):
    mensagem_usuario = "Arquivo invalido. Envie uma imagem em formato permitido (JPG, PNG, WEBP)."


class CamposObrigatoriosError(ErroDominio):
    mensagem_usuario = "Preencha todos os campos obrigatorios."
