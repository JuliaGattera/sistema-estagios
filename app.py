import streamlit as st
st.write("Streamlit versão:", st.__version__)
from supabase_client import supabase
from view.login import show_login_screen
from view.admin_panel import show_admin_panel
from view.estudante_panel import show_estudante_panel
from view.empresa_panel import show_empresa_panel

st.set_page_config(page_title="Sistema de Estágios", layout="centered")
st.title("Sistema de Estágios")

if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

def logout():
    st.session_state.user = None
    st.session_state.user_type = None
    st.experimental_rerun()

if st.session_state.user is None:
    show_login_screen(supabase)
elif st.session_state.user_type == "admin":
    show_admin_panel(supabase, logout)
elif st.session_state.user_type == "estudante":
    show_estudante_panel(supabase, logout)
elif st.session_state.user_type == "empresa":
    show_empresa_panel(supabase, logout)
