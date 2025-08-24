# app.py

import streamlit as st
from supabase_client import supabase
from view.login import show_login_screen
from view.admin_panel import show_admin_panel
from view.estudante_panel import show_estudante_panel
from view.empresa_panel import show_empresa_panel

# Configuração da página
st.set_page_config(page_title="Sistema de Estágios", layout="centered")
st.title("Sistema de Estágios")

# Inicializa session_state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# LOGIN / CADASTRO
if st.session_state.user is None:
    show_login_screen(supabase)  # Essa tela já trata login e cadastro de estudante/empresa

# PÓS-LOGIN: Painéis específicos
else:
    if st.session_state.user_type == "admin":
        show_admin_panel(supabase)
    elif st.session_state.user_type == "estudante":
        show_estudante_panel(supabase)
    elif st.session_state.user_type == "empresa":
        show_empresa_panel(supabase)
