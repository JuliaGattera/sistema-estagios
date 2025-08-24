import streamlit as st
from supabase_client import supabase
from login import show_login_screen  # (Vamos criar esse já já!)

st.set_page_config(page_title="Sistema de Estágios", layout="centered")
st.title("Sistema de Estágios")

if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

# LOGIN / CADASTRO
if st.session_state.user is None:
    show_login_screen(supabase)

# Em breve: painéis pós-login
elif st.session_state.user_type == "admin":
    st.write("Painel do administrador — em construção.")

elif st.session_state.user_type == "estudante":
    st.write("Painel do estudante — em construção.")

elif st.session_state.user_type == "empresa":
    st.write("Painel da empresa — em construção.")
