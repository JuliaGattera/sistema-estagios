import os
import streamlit as st
from supabase import create_client, Client

# Variáveis de ambiente
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

# Função auxiliar para autenticar
def autenticar_usuario(email, senha):
    try:
        user = supabase.auth.sign_in_with_password({"email": email, "password": senha})
        return user
    except Exception as e:
        st.error(f"Erro no login: {e}")
        return None

# Session State para manter o login
if "usuario" not in st.session_state:
    st.session_state.usuario = None
if "tipo_usuario" not in st.session_state:
    st.session_state.tipo_usuario = None

st.title("Sistema de Vagas para Estudantes - UNIUBE")

# Menu lateral
if st.session_state.usuario:
    st.sidebar.success(f"Logado como: {st.session_state.usuario['email']}")
    menu = st.sidebar.selectbox("Menu", ["Página Inicial", "Meu Perfil", "Ver Vagas", "Sair"])
else:
    menu = st.sidebar.selectbox("Menu", ["Login", "Cadastro"])

# CADASTRO
if menu == "Cadastro" and not st.session_state.usuario:
    st.subheader("Criar nova conta")
    tipo = st.selectbox("Tipo de usuário", ["Estudante", "Empresa"])
    nome = st.text_input("Nome")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Cadastrar"):
        try:
            user = supabase.auth.sign_up({"email": email, "password": senha})
            # Salvar no banco: estudantes ou empresas
            tabela = "estudantes" if tipo == "Estudante" else "empresas"
            dados = {"nome": nome, "email": email}
            supabase.table(tabela).insert(dados).execute()
            st.success("Cadastro realizado! Verifique seu e-mail.")
        except Exception as e:
            st.error(f"Erro: {e}")

# LOGIN
elif menu == "Login" and not st.session_state.usuario:
    st.subheader("Login")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = autenticar_usuario(email, senha)
        if user:
            st.session_state.usuario = user.user
            # Descobrir tipo de usuário
            est = supabase.table("estudantes").select("*").eq("email", email).execute()
            emp = supabase.table("empresas").select("*").eq("email", email).execute()
            if est.data:
                st.session_state.tipo_usuario = "estudante"
            elif emp.data:
                st.session_state.tipo_usuario = "empresa"
            st.rerun()

# SAIR
elif menu == "Sair":
    st.session_state.usuario = None
    st.session_state.tipo_usuario = None
    st.success("Você saiu da conta.")
    st.rerun()

# PÁGINAS LOGADAS
elif st.session_state.usuario:
    if menu == "Página Inicial":
        st.write(f"Bem-vindo, {st.session_state.tipo_usuario.title()}!")

    elif menu == "Meu Perfil":
        if st.session_state.tipo_usuario == "estudante":
            st.subheader("Perfil do Estudante")
            # Aqui você pode mostrar nome, curso, notas, etc.
        elif st.session_state.tipo_usuario == "empresa":
            st.subheader("Perfil da Empresa")
            # Aqui pode exibir nome, área, vagas criadas, etc.

    elif menu == "Ver Vagas" and st.session_state.tipo_usuario == "estudante":
        st.subheader("Vagas disponíveis para você")
        # Aqui você pode mostrar a lista de vagas do banco com botões de candidatura

    elif menu == "Ver Vagas" and st.session_state.tipo_usuario == "empresa":
        st.subheader("Minhas Vagas Criadas")
        # Aqui pode mostrar vagas criadas + botão para criar nova vaga
