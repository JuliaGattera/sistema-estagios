import os
import streamlit as st
from supabase import create_client, Client

# Configurações do Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Função para buscar tipo de usuário na tabela "usuarios"
def get_user_profile(user_id):
    response = supabase.table("usuarios").select("tipo_usuario").eq("id_auth", user_id).single().execute()
    if response.data:
        return response.data['tipo_usuario']
    return None

# Função para criar usuário na tabela "usuarios"
def create_user_profile(user_id, tipo_usuario):
    data = {"id_auth": user_id, "tipo_usuario": tipo_usuario}
    supabase.table("usuarios").insert(data).execute()

# Login admin fixo
def admin_login(username, password):
    # Defina seu login e senha fixos aqui
    return username == "admin" and password == "admin123"

# App começa aqui
st.title("Sistema de Vagas para Estudantes - UNIUBE")

menu = ["Login", "Cadastro"]
perfil = ["Estudante", "Empresa", "Admin"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Cadastro":
    st.subheader("Criar nova conta")
    tipo_usuario = st.selectbox("Tipo de usuário", ["Estudante", "Empresa"])
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        try:
            res = supabase.auth.sign_up({"email": email, "password": senha})
            if res.user:
                create_user_profile(res.user.id, tipo_usuario.lower())
                st.success("Cadastro realizado! Verifique seu e-mail para confirmar.")
            else:
                st.error("Erro ao criar usuário.")
        except Exception as e:
            st.error(f"Erro: {e}")

elif choice == "Login":
    st.subheader("Entrar na conta")
    tipo_usuario = st.selectbox("Perfil", perfil)
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Login"):
        if tipo_usuario == "Admin":
            if admin_login(email, senha):
                st.success("Login Admin realizado!")
                st.write("Bem-vindo, Admin!")
                # Aqui pode criar o menu/admin dashboard
            else:
                st.error("Usuário ou senha inválidos para Admin.")
        else:
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                if user.user:
                    perfil_usuario = get_user_profile(user.user.id)
                    if perfil_usuario != tipo_usuario.lower():
                        st.error(f"Perfil incorreto. Você selecionou {tipo_usuario}, mas seu cadastro é {perfil_usuario}.")
                    else:
                        st.success(f"Login {tipo_usuario} realizado com sucesso!")
                        st.write(f"Bem-vindo(a), {email}!")
                        # Aqui você pode colocar o menu específico de Estudante ou Empresa
                else:
                    st.error("Erro no login.")
            except Exception as e:
                st.error(f"Erro no login: {e}")
