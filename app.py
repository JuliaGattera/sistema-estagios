import streamlit as st
from supabase import create_client, Client

# Informações do Supabase
url = "https://aihxqgjzssffqnuarhsa.supabase.co"

key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFpaHhxZ2p6c3NmZnFudWFyaHNhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTU4ODQ0NDYsImV4cCI6MjA3MTQ2MDQ0Nn0.XOup2xySwS5m33vKFpeGeehV02-z-PjtiDe2IHAmQv8"

# Conecta ao Supabase
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
