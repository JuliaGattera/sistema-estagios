import streamlit as st
from view.empresa.criar_vaga import criar_vaga
from view.empresa.listar_vagas import listar_vagas_com_candidatos  # teu cuImport atualizado

def show_empresa_panel(supabase, logout_fn):
    user = st.session_state.user

    st.success(f"Login como Empresa realizado com sucesso! Bem-vindo, {user['nome']}")

    if st.button("Logout"):
        logout_fn()

    aba = st.radio("Menu da Empresa", [
        "Criar Nova Vaga",
        "Minhas Vagas"
    ])

    if aba == "Criar Nova Vaga":
        criar_vaga(supabase, user)

    elif aba == "Minhas Vagas":
        listar_vagas_com_candidatos(supabase, user)
