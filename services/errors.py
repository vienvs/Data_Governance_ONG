"""Hierarquia de excecoes de dominio.

Os servicos lancam estas excecoes; a camada de apresentacao (Streamlit)
captura ErroDominio e exibe a mensagem amigavel ao usuario.
"""
from __future__ import annotations


class ErroDominio(Exception):
    """Base de todas as excecoes de regra de negocio."""

    mensagem_usuario: str = "Ocorreu um erro ao processar a solicitação."

    def __init__(self, mensagem: str | None = None):
        super().__init__(mensagem or self.mensagem_usuario)
        self.mensagem_usuario = mensagem or self.mensagem_usuario


# Autenticacao e cadastro
class CredenciaisInvalidasError(ErroDominio):
    mensagem_usuario = "Email ou senha inválidos."


class CodigoAcessoInvalidoError(ErroDominio):
    mensagem_usuario = "Código de acesso da ONG inválido."


class EmailJaExistenteError(ErroDominio):
    mensagem_usuario = "Já existe uma conta com este email."


class EmailInvalidoError(ErroDominio):
    mensagem_usuario = "O email informado não tem um formato válido."


# Perfil de Dono
class CpfInvalidoError(ErroDominio):
    mensagem_usuario = "O CPF deve conter 11 dígitos numéricos."


class CpfJaExistenteError(ErroDominio):
    mensagem_usuario = "Este CPF já está cadastrado."


class PerfilDonoJaExisteError(ErroDominio):
    mensagem_usuario = "Você já possui um perfil de dono."


# Adocao
class AnimalIndisponivelError(ErroDominio):
    mensagem_usuario = "Este animal não está disponível para adoção."


class AnimalJaAdotadoError(ErroDominio):
    mensagem_usuario = "Este animal já foi adotado."


class SolicitacaoDuplicadaError(ErroDominio):
    mensagem_usuario = "Você já possui uma solicitação em análise para este animal."


class AceiteTermoObrigatorioError(ErroDominio):
    mensagem_usuario = "É necessário aceitar o Termo de Compromisso para concluir a adoção."


class SolicitacaoInexistenteError(ErroDominio):
    mensagem_usuario = "Solicitação inexistente ou não está em análise."


# Acesso e arquivos
class AcessoNegadoError(ErroDominio):
    mensagem_usuario = "Você não tem permissão para executar esta operação."


class ArquivoInvalidoError(ErroDominio):
    mensagem_usuario = "Arquivo inválido. Envie uma imagem em formato permitido (JPG, PNG, WEBP)."


class CamposObrigatoriosError(ErroDominio):
    mensagem_usuario = "Preencha todos os campos obrigatórios."
