import os
import streamlit as st
from supabase import create_client, Client

# Configurações iniciais
st.set_page_config(page_title="Sistema de Vagas", layout="centered")

# Pega as variáveis de ambiente do Supabase
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Cria cliente Supabase
supabase: Client = create_client(url, key)

# Título principal do app
st.title("Sistema de Vagas para Estudantes")

# Menu lateral
menu = ["Login", "Cadastro"]
choice = st.sidebar.selectbox("Menu", menu)

# --------------------
# TELA DE CADASTRO
# --------------------
if choice == "Cadastro":
    st.subheader("Criar nova conta")

    nome = st.text_input("Nome completo")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    matricula = st.text_input("Matrícula institucional")
    telefone = st.text_input("Telefone para contato")

    if st.button("Cadastrar"):
        if not nome or not email or not senha or not matricula:
            st.warning("Preencha todos os campos obrigatórios.")
        else:
            try:
                # Cria conta no Supabase Auth
                res = supabase.auth.sign_up({"email": email, "password": senha})

                # Se cadastro no Auth for bem-sucedido, salva dados na tabela "estudantes"
                if res.user:
                    supabase.table("estudantes").insert({
                        "nome": nome,
                        "email": email,
                        "matricula": matricula,
                        "telefone": telefone
                    }).execute()

                    st.success("Cadastro realizado com sucesso! Verifique seu e-mail para confirmar.")
            except Exception as e:
                st.error(f"Erro ao cadastrar: {e}")

# --------------------
# TELA DE LOGIN
# --------------------
elif choice == "Login":
    st.subheader("Entrar na conta")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Login"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            st.success("Login realizado com sucesso!")
            st.write("Usuário logado:", user.user.email)

            # Busca dados do estudante após login (baseado no email)
            dados_estudante = supabase.table("estudantes").select("*").eq("email", email).single().execute()

            if dados_estudante.data:
                st.subheader("Seu Perfil:")
                st.write("Nome:", dados_estudante.data["nome"])
                st.write("Matrícula:", dados_estudante.data["matricula"])
                st.write("Telefone:", dados_estudante.data["telefone"])
            else:
                st.warning("Cadastro incompleto. Nenhum dado encontrado para este e-mail.")

        except Exception as e:
            st.error(f"Erro no login: {e}")
