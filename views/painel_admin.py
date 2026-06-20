"""Painel administrativo: verificacao de documentos, CRUD de animais,
decisao de adocoes, agenda de castracao e auditoria. Restrito a admins."""
from __future__ import annotations

from contextlib import closing
from datetime import date

import streamlit as st

from app import session
from db.connection import get_connection
from models.entities import rotulo
from services import (
    file_storage,
    servico_adocao,
    servico_animais,
    servico_auditoria,
    servico_castracao,
)
from services.errors import ErroDominio
from repositories.dono_repository import DonoRepository


def render() -> None:
    admin = session.requer_admin()
    st.title("Painel Administrativo")
    st.caption(f"Sessao: {admin.nome} (administrador)")

    abas = st.tabs(["Donos / Documentos", "Animais", "Adocoes", "Castracoes / Agenda", "Auditoria"])
    with abas[0]:
        _aba_donos(admin)
    with abas[1]:
        _aba_animais()
    with abas[2]:
        _aba_adocoes(admin)
    with abas[3]:
        _aba_castracoes(admin)
    with abas[4]:
        _aba_auditoria()


# Aba: Donos
def _aba_donos(admin) -> None:
    st.subheader("Verificacao manual de documentos")
    filtro = st.selectbox("Filtrar por status", ["em_analise", "aprovado", "reprovado", "todos"],
                          format_func=lambda v: "Todos" if v == "todos" else rotulo("status_aprovacao", v))
    with closing(get_connection()) as conn:
        donos = DonoRepository(conn).listar(None if filtro == "todos" else filtro)

    if not donos:
        st.info("Nenhum dono encontrado para este filtro.")
        return

    for d in donos:
        with st.expander(f"{d['nome_usuario']} - CPF {d['cpf']} - {rotulo('status_aprovacao', d['status_aprovacao'])}"):
            st.write(
                f"**Email:** {d['email_usuario']}  \n"
                f"**Telefone:** {d['telefone']}  \n"
                f"**Endereco:** {d['endereco']}  \n"
                f"**Residencia:** {rotulo('tipo_residencia', d['tipo_residencia'])} "
                f"({'telada' if d['tem_tela'] else 'sem tela'})"
            )
            st.markdown("**Documentos enviados:**")
            cols = st.columns(3)
            for col, (titulo, caminho) in zip(
                cols,
                [("Documento", d["caminho_doc"]),
                 ("Comprovante", d["caminho_comprovante"]),
                 ("Tela", d["caminho_tela"])],
            ):
                with col:
                    st.caption(titulo)
                    if file_storage.arquivo_existe(caminho):
                        st.image(str(file_storage.caminho_absoluto(caminho)), use_container_width=True)
                    else:
                        st.warning("Imagem indisponivel")

            if d["status_aprovacao"] == "em_analise":
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Aprovar cadastro", key=f"apr_dono_{d['id']}"):
                        _decidir_dono(admin, d["id"], "aprovado")
                with c2:
                    if st.button("Reprovar cadastro", key=f"rep_dono_{d['id']}"):
                        _decidir_dono(admin, d["id"], "reprovado")


def _decidir_dono(admin, dono_id, status) -> None:
    with closing(get_connection()) as conn:
        DonoRepository(conn).atualizar_status(dono_id, status)
        servico_auditoria.registrar(conn, admin.id, f"dono_{status}", "dono", dono_id,
                                    f"Cadastro de dono {status}")
    st.success(f"Cadastro {rotulo('status_aprovacao', status).lower()}.")
    st.rerun()


# Aba: Animais
def _aba_animais() -> None:
    st.subheader("Gestao de animais (CRUD)")

    with st.expander("Cadastrar novo animal"):
        with st.form("novo_animal"):
            nome = st.text_input("Nome")
            c1, c2, c3 = st.columns(3)
            with c1:
                especie = st.selectbox("Especie", ["cao", "gato"],
                                       format_func=lambda v: rotulo("especie", v))
            with c2:
                sexo = st.selectbox("Sexo", ["macho", "femea"],
                                    format_func=lambda v: rotulo("sexo", v))
            with c3:
                idade = st.number_input("Idade (anos)", min_value=0, max_value=40, step=1)
            raca = st.text_input("Raca", value="SRD")
            descricao = st.text_area("Descricao")
            foto = st.file_uploader("Foto", type=["jpg", "jpeg", "png", "webp"])
            enviar = st.form_submit_button("Cadastrar animal")
        if enviar:
            if not nome.strip():
                st.error("Informe o nome do animal.")
            else:
                try:
                    with closing(get_connection()) as conn:
                        servico_animais.cadastrar_animal(conn, nome, especie, sexo,
                                                         idade, raca, descricao, foto)
                    st.success("Animal cadastrado!")
                    st.rerun()
                except (ErroDominio, ValueError) as e:
                    st.error(str(e))

    st.divider()
    filtro = st.selectbox("Filtrar por status", ["todos", "disponivel", "adotado"],
                          format_func=lambda v: "Todos" if v == "todos" else rotulo("status_animal", v))
    with closing(get_connection()) as conn:
        animais = servico_animais.listar_para_admin(conn, None if filtro == "todos" else filtro)

    for a in animais:
        with st.expander(f"{a['nome']} - {rotulo('especie', a['especie'])} - {rotulo('status_animal', a['status'])}"):
            with st.form(f"editar_animal_{a['id']}"):
                nome = st.text_input("Nome", value=a["nome"])
                c1, c2, c3 = st.columns(3)
                with c1:
                    especie = st.selectbox("Especie", ["cao", "gato"],
                                           index=0 if a["especie"] == "cao" else 1,
                                           format_func=lambda v: rotulo("especie", v))
                with c2:
                    sexo = st.selectbox("Sexo", ["macho", "femea"],
                                        index=0 if a["sexo"] == "macho" else 1,
                                        format_func=lambda v: rotulo("sexo", v))
                with c3:
                    idade = st.number_input("Idade", min_value=0, max_value=40,
                                            value=int(a["idade"]), step=1)
                raca = st.text_input("Raca", value=a["raca"] or "")
                descricao = st.text_area("Descricao", value=a["descricao"] or "")
                col_s, col_d = st.columns(2)
                with col_s:
                    salvar = st.form_submit_button("Salvar alteracoes")
                with col_d:
                    remover = st.form_submit_button("Remover animal")
            if salvar:
                with closing(get_connection()) as conn:
                    servico_animais.editar_animal(conn, a["id"], nome, especie, sexo,
                                                  idade, raca, descricao)
                st.success("Animal atualizado!")
                st.rerun()
            if remover:
                with closing(get_connection()) as conn:
                    servico_animais.remover_animal(conn, a["id"])
                st.warning("Animal removido.")
                st.rerun()


# Aba: Adocoes
def _aba_adocoes(admin) -> None:
    st.subheader("Solicitacoes de adocao")
    filtro = st.selectbox("Status", ["em_analise", "aprovado", "reprovado", "todos"],
                          key="filtro_adocao",
                          format_func=lambda v: "Todos" if v == "todos" else rotulo("status_aprovacao", v))
    with closing(get_connection()) as conn:
        solicitacoes = servico_adocao.listar_para_admin(conn, None if filtro == "todos" else filtro)

    if not solicitacoes:
        st.info("Nenhuma solicitacao para este filtro.")
        return

    for s in solicitacoes:
        with st.expander(f"#{s['id']} - {s['nome_adotante']} quer adotar {s['nome_animal']} "
                         f"({rotulo('status_aprovacao', s['status'])})"):
            respostas = servico_adocao.parse_respostas(s["respostas_questionario"])
            for pergunta, resposta in respostas.items():
                st.markdown(f"**{pergunta}**")
                st.write(resposta or "_(sem resposta)_")
            if s["observacoes_admin"]:
                st.caption(f"Observacoes: {s['observacoes_admin']}")

            if s["status"] == "em_analise":
                observacoes = st.text_area("Observacoes da decisao", key=f"obs_{s['id']}")
                aceite = st.checkbox("Adotante assinou o Termo de Compromisso", key=f"termo_{s['id']}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Aprovar adocao", key=f"apr_ado_{s['id']}"):
                        _aprovar_adocao(admin, s["id"], observacoes, aceite)
                with c2:
                    if st.button("Reprovar", key=f"rep_ado_{s['id']}"):
                        with closing(get_connection()) as conn:
                            servico_adocao.reprovar_adocao(conn, s["id"], admin.id, observacoes)
                        st.warning("Solicitacao reprovada.")
                        st.rerun()


def _aprovar_adocao(admin, solicitacao_id, observacoes, aceite) -> None:
    try:
        with closing(get_connection()) as conn:
            servico_adocao.aprovar_adocao(conn, solicitacao_id, admin.id, observacoes, aceite)
        st.success("Adocao aprovada! O animal foi marcado como adotado.")
        st.rerun()
    except ErroDominio as e:
        st.error(e.mensagem_usuario)


# Aba: Castracoes
def _aba_castracoes(admin) -> None:
    st.subheader("Castracoes e agenda")

    with closing(get_connection()) as conn:
        agenda = servico_castracao.listar_agenda(conn)
    if agenda:
        st.markdown("**Proximos procedimentos agendados:**")
        for s in agenda:
            st.write(f"- {s['data_agendada']} - {s['nome_pet']} ({rotulo('especie', s['especie'])}), "
                     f"tutor {s['nome_tutor']}")
        st.divider()

    filtro = st.selectbox("Status", ["em_analise", "aprovado", "reprovado", "todos"],
                          key="filtro_castracao",
                          format_func=lambda v: "Todos" if v == "todos" else rotulo("status_aprovacao", v))
    with closing(get_connection()) as conn:
        solicitacoes = servico_castracao.listar_para_admin(conn, None if filtro == "todos" else filtro)

    if not solicitacoes:
        st.info("Nenhuma solicitacao para este filtro.")
        return

    for s in solicitacoes:
        with st.expander(f"#{s['id']} - {s['nome_pet']} ({rotulo('especie', s['especie'])}) - "
                         f"{rotulo('status_aprovacao', s['status'])}"):
            st.write(
                f"**Tutor:** {s['nome_tutor']}  \n"
                f"**Telefone:** {s['telefone']}  \n"
                f"**Endereco:** {s['endereco']}  \n"
                f"**Solicitado em:** {s['data_solicitacao']}"
            )
            if s["status"] == "em_analise":
                data_proc = st.date_input("Data do procedimento (se aprovar)",
                                          min_value=date.today(), key=f"data_{s['id']}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Aprovar e agendar", key=f"apr_cas_{s['id']}"):
                        with closing(get_connection()) as conn:
                            servico_castracao.atualizar_status_castracao(
                                conn, s["id"], admin.id, "aprovado", data_proc.isoformat())
                        st.success(f"Castracao aprovada e agendada para {data_proc.isoformat()}.")
                        st.rerun()
                with c2:
                    if st.button("Reprovar", key=f"rep_cas_{s['id']}"):
                        with closing(get_connection()) as conn:
                            servico_castracao.atualizar_status_castracao(
                                conn, s["id"], admin.id, "reprovado")
                        st.warning("Solicitacao reprovada.")
                        st.rerun()


# Aba: Auditoria
def _aba_auditoria() -> None:
    st.subheader("Log de auditoria")
    with closing(get_connection()) as conn:
        eventos = servico_auditoria.listar_eventos(conn)
    if not eventos:
        st.info("Nenhum evento registrado.")
        return
    linhas = []
    for e in eventos:
        linhas.append({
            "Data/Hora": e["data_hora"],
            "Usuario": e["nome_usuario"] or e["usuario_id"],
            "Acao": e["acao"],
            "Entidade": e["entidade"],
            "Registro": e["registro_id"],
            "Detalhe": e["detalhe"],
        })
    st.dataframe(linhas, use_container_width=True)
