import sqlite3
from pathlib import Path
from datetime import date
import pandas as pd
import streamlit as st

from banco import conectar, criar_banco, criar_usuarios_iniciais

# Inicialização única e segura do banco.
criar_banco()
criar_usuarios_iniciais()

st.set_page_config(
    page_title="Sistema de Reserva de Salas",
    page_icon="🏫",
    layout="wide",
)


def limpar_login():
    st.session_state.logado = False
    st.session_state.usuario_nome = ""
    st.session_state.usuario_tipo = ""


# Estado da sessão
st.session_state.setdefault("logado", False)
st.session_state.setdefault("usuario_nome", "")
st.session_state.setdefault("usuario_tipo", "")


# -------------------------
# LOGIN
# -------------------------
if not st.session_state.logado:
    st.title("🔐 Login")
    st.write("Entre com seu e-mail e senha.")

    with st.form("form_login", clear_on_submit=False):
        email_login = st.text_input("E-mail", key="login_email")
        senha_login = st.text_input("Senha", type="password", key="login_senha")
        entrar = st.form_submit_button("Entrar", use_container_width=True)

    if entrar:
        email = email_login.strip().lower()
        with conectar() as conexao:
            usuario = conexao.execute(
                """
                SELECT nome, tipo
                FROM usuarios
                WHERE lower(email) = ? AND senha = ?
                """,
                (email, senha_login),
            ).fetchone()

        if usuario:
            st.session_state.logado = True
            st.session_state.usuario_nome = usuario[0]
            st.session_state.usuario_tipo = usuario[1]
            st.rerun()
        else:
            st.error("E-mail ou senha inválidos.")

    st.info("Usuários de teste: admin@faculdade.com / 1234 e joao@faculdade.com / 1234")
    st.stop()


# -------------------------
# CABEÇALHO / MENU
# -------------------------
st.title("🏫 Sistema de Reserva de Salas")
st.caption("Gerenciamento de salas e solicitações de reservas.")

st.sidebar.write(f"👤 **{st.session_state.usuario_nome}**")
st.sidebar.write(f"Perfil: **{st.session_state.usuario_tipo}**")
st.sidebar.divider()

if st.session_state.usuario_tipo == "Administrador":
    opcoes_menu = ["Início", "Salas", "Professores", "Reservas", "Administração"]
else:
    opcoes_menu = ["Início", "Reservas"]

pagina = st.sidebar.radio("Menu", opcoes_menu, key="menu_principal")
st.sidebar.divider()

if st.sidebar.button("🚪 Sair", use_container_width=True, key="btn_sair"):
    limpar_login()
    st.rerun()


# -------------------------
# INÍCIO
# -------------------------
if pagina == "Início":
    st.header("📊 Painel Principal")

    if st.session_state.usuario_tipo == "Professor":
        with conectar() as conexao:
            professor = conexao.execute(
                "SELECT id FROM professores WHERE lower(email) = lower(?)",
                (f"{st.session_state.usuario_nome}",),
            ).fetchone()
            # O nome é usado como fallback para compatibilidade com o banco antigo.
            if professor is None:
                professor = conexao.execute(
                    "SELECT id FROM professores WHERE nome = ?",
                    (st.session_state.usuario_nome,),
                ).fetchone()

            if professor:
                pid = professor[0]
                total_minhas = conexao.execute("SELECT COUNT(*) FROM reservas WHERE professor_id = ?", (pid,)).fetchone()[0]
                total_pendentes = conexao.execute("SELECT COUNT(*) FROM reservas WHERE professor_id = ? AND status = 'Pendente'", (pid,)).fetchone()[0]
                total_aprovadas = conexao.execute("SELECT COUNT(*) FROM reservas WHERE professor_id = ? AND status = 'Aprovada'", (pid,)).fetchone()[0]
                total_canceladas = conexao.execute("SELECT COUNT(*) FROM reservas WHERE professor_id = ? AND status = 'Cancelada'", (pid,)).fetchone()[0]
            else:
                total_minhas = total_pendentes = total_aprovadas = total_canceladas = 0

        st.subheader(f"👨‍🏫 Bem-vindo, {st.session_state.usuario_nome}")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("📅 Minhas Reservas", total_minhas)
        c2.metric("⏳ Pendentes", total_pendentes)
        c3.metric("✅ Aprovadas", total_aprovadas)
        c4.metric("🚫 Canceladas", total_canceladas)
        st.divider()
        st.info("Use o menu lateral para realizar novas reservas e acompanhar suas solicitações.")
    else:
        with conectar() as conexao:
            total_salas = conexao.execute("SELECT COUNT(*) FROM salas").fetchone()[0]
            total_professores = conexao.execute("SELECT COUNT(*) FROM professores").fetchone()[0]
            total_pendentes = conexao.execute("SELECT COUNT(*) FROM reservas WHERE status = 'Pendente'").fetchone()[0]
            total_aprovadas = conexao.execute("SELECT COUNT(*) FROM reservas WHERE status = 'Aprovada'").fetchone()[0]

        st.subheader("⚙️ Visão do Administrador")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏫 Salas", total_salas)
        c2.metric("👨‍🏫 Professores", total_professores)
        c3.metric("⏳ Pendentes", total_pendentes)
        c4.metric("✅ Aprovadas", total_aprovadas)
        st.divider()
        st.info("Use o menu lateral para cadastrar salas, professores, gerenciar reservas e analisar solicitações.")


# -------------------------
# SALAS
# -------------------------
elif pagina == "Salas":
    st.header("🏫 Cadastro de Salas")

    with st.form("form_sala"):
        nome = st.text_input("Nome da sala", key="sala_nome_nova")
        capacidade = st.number_input("Capacidade", min_value=1, value=1, step=1, key="sala_capacidade_nova")
        localizacao = st.text_input("Localização", key="sala_localizacao_nova")
        projetor = st.selectbox("Possui projetor?", ["Sim", "Não"], key="sala_projetor_nova")
        computadores = st.number_input("Quantidade de computadores", min_value=0, value=0, step=1, key="sala_computadores_nova")
        cadastrar = st.form_submit_button("Cadastrar Sala", use_container_width=True)

    if cadastrar:
        if not nome.strip() or not localizacao.strip():
            st.warning("Preencha nome e localização.")
        else:
            with conectar() as conexao:
                conexao.execute(
                    """
                    INSERT INTO salas (nome, capacidade, localizacao, projetor, computadores, status)
                    VALUES (?, ?, ?, ?, ?, 'Disponível')
                    """,
                    (nome.strip(), int(capacidade), localizacao.strip(), projetor, int(computadores)),
                )
                conexao.commit()
            st.success("Sala cadastrada com sucesso!")
            st.rerun()

    st.divider()
    st.subheader("📋 Salas cadastradas")
    with conectar() as conexao:
        salas = pd.read_sql_query("SELECT * FROM salas ORDER BY nome", conexao)

    if salas.empty:
        st.info("Nenhuma sala cadastrada.")
    else:
        st.dataframe(salas, use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("✏️ Editar ou Excluir Sala")

        sala_id = st.selectbox(
            "Selecione uma sala",
            salas["id"].tolist(),
            format_func=lambda x: salas.loc[salas["id"] == x, "nome"].iloc[0],
            key="editar_sala_id",
        )
        dados = salas[salas["id"] == sala_id].iloc[0]

        novo_nome = st.text_input("Novo nome", value=str(dados["nome"]), key=f"novo_nome_sala_{sala_id}")
        nova_capacidade = st.number_input("Nova capacidade", min_value=1, value=int(dados["capacidade"]), step=1, key=f"nova_capacidade_{sala_id}")
        nova_localizacao = st.text_input("Nova localização", value=str(dados["localizacao"]), key=f"nova_localizacao_{sala_id}")
        novo_projetor = st.selectbox("Possui projetor?", ["Sim", "Não"], index=0 if dados["projetor"] == "Sim" else 1, key=f"novo_projetor_{sala_id}")
        novos_computadores = st.number_input("Quantidade de computadores", min_value=0, value=int(dados["computadores"] or 0), step=1, key=f"novos_computadores_{sala_id}")

        c1, c2 = st.columns(2)
        if c1.button("💾 Salvar Alterações", use_container_width=True, key=f"salvar_sala_{sala_id}"):
            if not novo_nome.strip() or not nova_localizacao.strip():
                st.warning("Nome e localização não podem ficar vazios.")
            else:
                with conectar() as conexao:
                    conexao.execute(
                        """
                        UPDATE salas SET nome=?, capacidade=?, localizacao=?, projetor=?, computadores=?
                        WHERE id=?
                        """,
                        (novo_nome.strip(), int(nova_capacidade), nova_localizacao.strip(), novo_projetor, int(novos_computadores), int(sala_id)),
                    )
                    conexao.commit()
                st.success("Sala atualizada com sucesso!")
                st.rerun()

        if c2.button("🗑️ Excluir Sala", use_container_width=True, key=f"excluir_sala_{sala_id}"):
            with conectar() as conexao:
                total = conexao.execute("SELECT COUNT(*) FROM reservas WHERE sala_id = ?", (int(sala_id),)).fetchone()[0]
                if total:
                    st.error("Não é possível excluir esta sala porque ela possui reservas vinculadas.")
                else:
                    conexao.execute("DELETE FROM salas WHERE id = ?", (int(sala_id),))
                    conexao.commit()
                    st.success("Sala excluída com sucesso!")
                    st.rerun()


# -------------------------
# PROFESSORES
# -------------------------
elif pagina == "Professores":
    st.header("👨‍🏫 Cadastro de Professores")

    with st.form("form_professor"):
        nome = st.text_input("Nome do professor", key="prof_nome_novo")
        email = st.text_input("E-mail", key="prof_email_novo")
        departamento = st.text_input("Departamento / Curso", key="prof_departamento_novo")
        cadastrar = st.form_submit_button("Cadastrar Professor", use_container_width=True)

    if cadastrar:
        if not nome.strip() or not email.strip() or not departamento.strip():
            st.warning("Preencha todos os campos.")
        else:
            try:
                with conectar() as conexao:
                    conexao.execute(
                        "INSERT INTO professores (nome, email, departamento) VALUES (?, ?, ?)",
                        (nome.strip(), email.strip().lower(), departamento.strip()),
                    )
                    conexao.commit()
                st.success("Professor cadastrado com sucesso!")
                st.rerun()
            except sqlite3.IntegrityError:
                st.error("Já existe um professor cadastrado com esse e-mail.")

    st.divider()
    st.subheader("📋 Professores cadastrados")
    with conectar() as conexao:
        professores = pd.read_sql_query("SELECT * FROM professores ORDER BY nome", conexao)

    if professores.empty:
        st.info("Nenhum professor cadastrado.")
    else:
        st.dataframe(professores, use_container_width=True, hide_index=True)
        st.divider()
        st.subheader("✏️ Editar ou Excluir Professor")
        professor_id = st.selectbox(
            "Selecione um professor",
            professores["id"].tolist(),
            format_func=lambda x: professores.loc[professores["id"] == x, "nome"].iloc[0],
            key="editar_professor_id",
        )
        dados = professores[professores["id"] == professor_id].iloc[0]

        novo_nome = st.text_input("Nome", value=str(dados["nome"]), key=f"novo_nome_prof_{professor_id}")
        novo_email = st.text_input("E-mail", value=str(dados["email"]), key=f"novo_email_prof_{professor_id}")
        novo_dep = st.text_input("Departamento / Curso", value=str(dados["departamento"]), key=f"novo_dep_prof_{professor_id}")

        c1, c2 = st.columns(2)
        if c1.button("💾 Salvar Alterações", use_container_width=True, key=f"salvar_prof_{professor_id}"):
            if not novo_nome.strip() or not novo_email.strip() or not novo_dep.strip():
                st.warning("Nenhum campo pode ficar vazio.")
            else:
                try:
                    with conectar() as conexao:
                        conexao.execute(
                            "UPDATE professores SET nome=?, email=?, departamento=? WHERE id=?",
                            (novo_nome.strip(), novo_email.strip().lower(), novo_dep.strip(), int(professor_id)),
                        )
                        conexao.commit()
                    st.success("Professor atualizado com sucesso!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Este e-mail já está sendo utilizado por outro professor.")

        if c2.button("🗑️ Excluir Professor", use_container_width=True, key=f"excluir_prof_{professor_id}"):
            with conectar() as conexao:
                total = conexao.execute("SELECT COUNT(*) FROM reservas WHERE professor_id = ?", (int(professor_id),)).fetchone()[0]
                if total:
                    st.error("Não é possível excluir este professor porque existem reservas vinculadas a ele.")
                else:
                    conexao.execute("DELETE FROM professores WHERE id = ?", (int(professor_id),))
                    conexao.commit()
                    st.success("Professor excluído com sucesso!")
                    st.rerun()


# -------------------------
# RESERVAS
# -------------------------
elif pagina == "Reservas":
    st.header("📅 Solicitação de Reserva")

    with conectar() as conexao:
        professores = pd.read_sql_query("SELECT * FROM professores ORDER BY nome", conexao)
        salas = pd.read_sql_query("SELECT * FROM salas WHERE status = 'Disponível' ORDER BY nome", conexao)

    if professores.empty or salas.empty:
        st.warning("É necessário cadastrar pelo menos um professor e uma sala disponível antes de realizar uma reserva.")
    else:
        with st.form("form_reserva"):
            if st.session_state.usuario_tipo == "Professor":
                professor = professores[professores["nome"] == st.session_state.usuario_nome]
                if professor.empty:
                    st.error("Seu usuário não está vinculado a um professor cadastrado.")
                    st.stop()
                professor_id = int(professor.iloc[0]["id"])
                st.text_input("Professor", value=st.session_state.usuario_nome, disabled=True)
            else:
                professor_id = int(st.selectbox("Professor", professores["id"].tolist(), format_func=lambda x: professores.loc[professores["id"] == x, "nome"].iloc[0], key="reserva_professor_id"))

            sala_id = int(st.selectbox("Sala", salas["id"].tolist(), format_func=lambda x: salas.loc[salas["id"] == x, "nome"].iloc[0], key="reserva_sala_id"))
            data = st.date_input("Data da reserva", min_value=date.today(), key="reserva_data")
            c1, c2 = st.columns(2)
            horario_inicio = c1.time_input("Horário de início", key="reserva_inicio")
            horario_fim = c2.time_input("Horário de término", key="reserva_fim")
            finalidade = st.text_area("Finalidade da reserva", placeholder="Ex.: Aula de Redes de Computadores", key="reserva_finalidade")
            reservar = st.form_submit_button("Solicitar Reserva", use_container_width=True)

        if reservar:
            if horario_fim <= horario_inicio:
                st.error("O horário de término deve ser posterior ao horário de início.")
            elif not finalidade.strip():
                st.warning("Informe a finalidade da reserva.")
            else:
                data_texto = data.strftime("%Y-%m-%d")
                inicio_texto = horario_inicio.strftime("%H:%M")
                fim_texto = horario_fim.strftime("%H:%M")
                with conectar() as conexao:
                    conflito = conexao.execute(
                        """
                        SELECT COUNT(*) FROM reservas
                        WHERE sala_id = ? AND data = ?
                        AND status NOT IN ('Recusada', 'Cancelada')
                        AND horario_inicio < ? AND horario_fim > ?
                        """,
                        (sala_id, data_texto, fim_texto, inicio_texto),
                    ).fetchone()[0]
                    if conflito:
                        st.error("❌ Esta sala já possui uma reserva nesse período.")
                    else:
                        conexao.execute(
                            """
                            INSERT INTO reservas
                            (professor_id, sala_id, data, horario_inicio, horario_fim, finalidade, status)
                            VALUES (?, ?, ?, ?, ?, ?, 'Pendente')
                            """,
                            (professor_id, sala_id, data_texto, inicio_texto, fim_texto, finalidade.strip()),
                        )
                        conexao.commit()
                        st.success("✅ Reserva solicitada com sucesso!")
                        st.rerun()

    st.divider()
    st.subheader("📋 Reservas realizadas")
    sql = """
        SELECT r.id, p.nome AS professor, s.nome AS sala, r.data,
               r.horario_inicio AS inicio, r.horario_fim AS fim,
               r.finalidade, r.status
        FROM reservas r
        INNER JOIN professores p ON r.professor_id = p.id
        INNER JOIN salas s ON r.sala_id = s.id
    """
    params = ()
    if st.session_state.usuario_tipo == "Professor":
        sql += " WHERE p.nome = ?"
        params = (st.session_state.usuario_nome,)
    sql += " ORDER BY r.data, r.horario_inicio"

    with conectar() as conexao:
        reservas = pd.read_sql_query(sql, conexao, params=params)

    if reservas.empty:
        st.info("Nenhuma reserva realizada.")
    else:
        st.dataframe(reservas, use_container_width=True, hide_index=True)
        ativas = reservas[reservas["status"].isin(["Pendente", "Aprovada"])]
        st.divider()
        st.subheader("🚫 Cancelar Reserva")
        if ativas.empty:
            st.info("Não existem reservas disponíveis para cancelamento.")
        else:
            opcoes = {
                f"Reserva #{r.id} - {r.professor} - {r.sala} - {r.data} - {r.inicio} às {r.fim}": int(r.id)
                for r in ativas.itertuples()
            }
            selecionada = st.selectbox("Selecione a reserva que deseja cancelar", list(opcoes), key="cancelar_reserva_id")
            confirmar = st.checkbox("Confirmo que desejo cancelar esta reserva.", key="confirmar_cancelamento")
            if st.button("🚫 Cancelar Reserva", use_container_width=True, key="btn_cancelar_reserva"):
                if not confirmar:
                    st.warning("Marque a confirmação antes de cancelar.")
                else:
                    with conectar() as conexao:
                        conexao.execute("UPDATE reservas SET status='Cancelada' WHERE id=?", (opcoes[selecionada],))
                        conexao.commit()
                    st.success("Reserva cancelada com sucesso!")
                    st.rerun()


# -------------------------
# ADMINISTRAÇÃO
# -------------------------
elif pagina == "Administração":
    st.header("⚙️ Administração de Reservas")

    with conectar() as conexao:
        pendentes = pd.read_sql_query(
            """
            SELECT r.id, p.nome AS professor, s.nome AS sala, r.data,
                   r.horario_inicio, r.horario_fim, r.finalidade, r.status
            FROM reservas r
            INNER JOIN professores p ON r.professor_id = p.id
            INNER JOIN salas s ON r.sala_id = s.id
            WHERE r.status = 'Pendente'
            ORDER BY r.data, r.horario_inicio
            """,
            conexao,
        )

    if pendentes.empty:
        st.success("Não existem reservas pendentes.")
    else:
        st.subheader("📋 Solicitações pendentes")
        for reserva in pendentes.itertuples():
            with st.container(border=True):
                st.write(f"### Reserva #{reserva.id}")
                st.write(f"👨‍🏫 **Professor:** {reserva.professor}")
                st.write(f"🏫 **Sala:** {reserva.sala}")
                st.write(f"📅 **Data:** {reserva.data}")
                st.write(f"🕐 **Horário:** {reserva.horario_inicio} até {reserva.horario_fim}")
                st.write(f"📝 **Finalidade:** {reserva.finalidade}")
                c1, c2 = st.columns(2)
                if c1.button("✅ Aprovar", use_container_width=True, key=f"aprovar_{reserva.id}"):
                    with conectar() as conexao:
                        # Revalida conflito antes de aprovar.
                        conflito = conexao.execute(
                            """
                            SELECT COUNT(*) FROM reservas
                            WHERE sala_id = (SELECT sala_id FROM reservas WHERE id = ?)
                              AND data = (SELECT data FROM reservas WHERE id = ?)
                              AND id <> ?
                              AND status = 'Aprovada'
                              AND horario_inicio < (SELECT horario_fim FROM reservas WHERE id = ?)
                              AND horario_fim > (SELECT horario_inicio FROM reservas WHERE id = ?)
                            """,
                            (reserva.id, reserva.id, reserva.id, reserva.id, reserva.id),
                        ).fetchone()[0]
                        if conflito:
                            st.error("Não foi possível aprovar: existe outra reserva aprovada no mesmo período.")
                        else:
                            conexao.execute("UPDATE reservas SET status='Aprovada' WHERE id=?", (reserva.id,))
                            conexao.commit()
                            st.success("Reserva aprovada!")
                            st.rerun()
                if c2.button("❌ Recusar", use_container_width=True, key=f"recusar_{reserva.id}"):
                    with conectar() as conexao:
                        conexao.execute("UPDATE reservas SET status='Recusada' WHERE id=?", (reserva.id,))
                        conexao.commit()
                    st.warning("Reserva recusada!")
                    st.rerun()
