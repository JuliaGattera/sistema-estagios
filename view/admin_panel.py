# view/admin_panel.py
import streamlit as st

def show_admin_panel(supabase, logout_func):
    st.success(f"Login como Administrador realizado com sucesso! Bem-vindo, {st.session_state.user['email']}")

    if st.button("Logout"):
        logout_func()

    aba_admin = st.radio("Menu do Administrador", [
        "Gerenciar Cursos",
        "Gerenciar Disciplinas",
        "Gerenciar Estudantes",
        "Gerenciar Empresas",
        "Gerenciar Vagas"
    ])

    if aba_admin == "Gerenciar Cursos":
        st.subheader("Cadastro de Cursos")
        nome_curso = st.text_input("Nome do Curso")
        if st.button("Adicionar Curso"):
            if nome_curso.strip() == "":
                st.warning("Informe o nome do curso.")
            else:
                try:
                    supabase.table("cursos").insert({"nome": nome_curso}).execute()
                    st.success(f"Curso '{nome_curso}' adicionado com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao adicionar curso: {e}")

    elif aba_admin == "Gerenciar Disciplinas":
        st.subheader("Gerenciar Disciplinas")
        st.info("Funcionalidade a implementar.")

    elif aba_admin == "Gerenciar Estudantes":
        st.subheader("Gerenciar Estudantes")
        st.info("Funcionalidade a implementar.")

    elif aba_admin == "Gerenciar Empresas":
        st.subheader("Gerenciar Empresas")
        st.info("Funcionalidade a implementar.")

    elif aba_admin == "Gerenciar Vagas":
        st.subheader("Gerenciar Vagas")
        st.info("Funcionalidade a implementar.")
