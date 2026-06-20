"""Ponto de entrada da aplicacao Streamlit.

Executa o bootstrap do banco, monta a navegacao com base no perfil (RBAC)
e roteia para as paginas (views). Rode com:  streamlit run app/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path (permite rodar de qualquer lugar)
RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from app import session  # noqa: E402
from db.connection import inicializar_banco  # noqa: E402
from views import adocao, auth, catalogo, castracao, painel_admin, perfil_dono  # noqa: E402


@st.cache_resource
def _bootstrap() -> bool:
    """Cria o schema do banco uma unica vez por sessao do servidor."""
    inicializar_banco()
    return True


# Paginas disponiveis por perfil
PAGINAS_PUBLICAS = {
    "Catalogo de animais": catalogo.render,
}
PAGINAS_USUARIO = {
    "Meu perfil": perfil_dono.render,
    "Adocao": adocao.render,
    "Castracao": castracao.render,
}
PAGINAS_ADMIN = {
    "Painel administrativo": painel_admin.render,
}


def main() -> None:
    st.set_page_config(page_title="ONG de Adocao", layout="wide")
    _bootstrap()

    usuario = session.usuario_atual()

    # Nao autenticado: tela de login/cadastro + catalogo publico
    if usuario is None:
        with st.sidebar:
            st.header("ONG de Adocao")
            escolha = st.radio("Navegacao", ["Acesso", "Catalogo de animais"])
        if escolha == "Catalogo de animais":
            catalogo.render()
        else:
            auth.render()
        return

    # Autenticado: monta o menu conforme o perfil
    paginas = {**PAGINAS_PUBLICAS, **PAGINAS_USUARIO}
    if usuario.is_admin:
        paginas = {**paginas, **PAGINAS_ADMIN}

    with st.sidebar:
        st.header("ONG de Adocao")
        st.write(f"Ola, **{usuario.nome}**")
        st.caption("Administrador" if usuario.is_admin else "Usuario comum")
        escolha = st.radio("Navegacao", list(paginas.keys()))
        st.divider()
        if st.button("Sair"):
            session.encerrar_sessao()
            st.rerun()

    # Roteamento com guarda de erros de acesso
    try:
        paginas[escolha]()
    except Exception as e:  # noqa: BLE001 - exibe erro amigavel sem derrubar a app
        st.error(f"Nao foi possivel abrir a pagina: {e}")


if __name__ == "__main__":
    main()
