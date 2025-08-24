# view/empresa_panel.py
import streamlit as st

def show_empresa_panel(supabase, logout_func):
    user = st.session_state.user
    st.success(f"Login como Empresa realizado com sucesso! Bem-vindo, {user['nome']}")

    if st.button("Logout"):
        logout_func()

    st.info("Funcionalidades da empresa ainda serão implementadas.")
