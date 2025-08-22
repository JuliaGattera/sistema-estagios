import os
import streamlit as st
from supabase import create_client, Client

# Pega as variáveis de ambiente
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Cria cliente do supabase
supabase: Client = create_client(url, key)

st.title("Sistema de Vagas para Estudantes")

# Interface de login
menu = ["Login", "Cadastro"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Cadastro":
    st.subheader("Criar nova conta")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        try:
            res = supabase.auth.sign_up({"email": email, "password": senha})
            st.success("Cadastro realizado! Verifique seu e-mail para confirmar.")
        except Exception as e:
            st.error(f"Erro: {e}")

elif choice == "Login":
    st.subheader("Entrar na conta")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Login"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            st.success("Login realizado com sucesso!")
            st.write("Usuário:", user.user.email)
        except Exception as e:
            st.error(f"Erro no login: {e}")
