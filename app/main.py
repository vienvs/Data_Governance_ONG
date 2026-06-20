"""Ponto de entrada da aplicacao Streamlit.

Executa o bootstrap do banco, aplica o estilo visual, monta a navegacao em
estilo de site conforme o perfil (RBAC) e roteia para as paginas (views).
Rode com:  streamlit run app/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from app import session, ui  # noqa: E402
from db.connection import inicializar_banco  # noqa: E402
from views import adocao, auth, catalogo, castracao, painel_admin, perfil_dono  # noqa: E402

try:
    from streamlit_option_menu import option_menu
    TEM_OPTION_MENU = True
except Exception:
    TEM_OPTION_MENU = False


@st.cache_resource
def _bootstrap() -> bool:
    """Cria o schema do banco uma unica vez por sessao do servidor."""
    inicializar_banco()
    return True


def _menu(titulo, labels, icones, chave):
    """Mostra um menu de navegacao. Usa option_menu se disponivel; senao radio."""
    if TEM_OPTION_MENU:
        return option_menu(
            menu_title=titulo,
            options=labels,
            icons=icones,
            menu_icon="house-heart",
            default_index=0,
            key=chave,
            styles={
                "container": {"background-color": "transparent", "padding": "0"},
                "icon": {"color": "#F4845F", "font-size": "17px"},
                "nav-link": {
                    "font-size": "15px",
                    "font-weight": "600",
                    "border-radius": "10px",
                    "margin": "3px 0",
                    "--hover-color": "#FFE3D3",
                },
                "nav-link-selected": {"background-color": "#F4845F", "color": "white"},
            },
        )
    return st.radio(titulo, labels, key=chave)


def _pagina_publica() -> None:
    paginas = {"Início": None, "Catálogo de animais": catalogo.render}
    icones = ["door-open", "heart"]
    with st.sidebar:
        st.markdown("### Cuida ONG")
        st.caption("Adoção responsável de cães e gatos")
        escolha = _menu("Menu", list(paginas.keys()), icones, "menu_publico")
    if escolha == "Catálogo de animais":
        catalogo.render()
    else:
        auth.render()


def _pagina_autenticada(usuario) -> None:
    paginas = {
        "Catálogo de animais": ("heart", catalogo.render),
        "Meu perfil": ("person-vcard", perfil_dono.render),
        "Adoção": ("house-heart", adocao.render),
        "Castração": ("calendar-check", castracao.render),
    }
    if usuario.is_admin:
        paginas["Painel administrativo"] = ("shield-lock", painel_admin.render)

    labels = list(paginas.keys())
    icones = []
    for label in labels:
        icones.append(paginas[label][0])

    with st.sidebar:
        st.markdown("### Cuida ONG")
        st.caption(f"Olá, {usuario.nome}")
        papel = "Administrador" if usuario.is_admin else "Usuário comum"
        st.markdown(ui.badge(papel, "ok" if usuario.is_admin else "wait"),
                    unsafe_allow_html=True)
        st.write("")
        escolha = _menu("Menu", labels, icones, "menu_app")
        st.write("")
        if st.button("Sair", use_container_width=True):
            session.encerrar_sessao()
            st.rerun()

    try:
        paginas[escolha][1]()
    except Exception as e:  # noqa: BLE001
        st.error(f"Nao foi possivel abrir a pagina: {e}")


def main() -> None:
    st.set_page_config(page_title="Cuida ONG - Adocao", layout="wide")
    ui.aplicar_estilo()
    _bootstrap()

    usuario = session.usuario_atual()
    if usuario is None:
        _pagina_publica()
    else:
        _pagina_autenticada(usuario)


if __name__ == "__main__":
    main()
