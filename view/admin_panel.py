import streamlit as st
from view.admin.cursos import gerenciar_cursos
from view.admin.disciplinas import gerenciar_disciplinas
from view.admin.estudantes import gerenciar_estudantes
from view.admin.empresas import gerenciar_empresas
from view.admin.vagas import gerenciar_vagas

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
        gerenciar_cursos(supabase)
    elif aba_admin == "Gerenciar Disciplinas":
        gerenciar_disciplinas(supabase)
    elif aba_admin == "Gerenciar Estudantes":
        gerenciar_estudantes(supabase)
    elif aba_admin == "Gerenciar Empresas":
        gerenciar_empresas(supabase)
    elif aba_admin == "Gerenciar Vagas":
        gerenciar_vagas(supabase)
