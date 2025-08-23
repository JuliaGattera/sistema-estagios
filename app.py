import os
import streamlit as st
from supabase import create_client, Client

# Configurações iniciais
st.set_page_config(page_title="Sistema de Estágios", layout="centered")
st.title("Sistema de Estágios")

# Variáveis de ambiente
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Menu lateral
menu = ["Login", "Cadastro"]
choice = st.sidebar.selectbox("Menu", menu)

# === CADASTRO ===
if choice == "Cadastro":
    st.subheader("Cadastro de Usuário")
    tipo_usuario = st.selectbox("Tipo de usuário", ["Estudante", "Empresa"])

    # CADASTRO DE ESTUDANTE
    if tipo_usuario == "Estudante":
        matricula = st.text_input("Matrícula")
        email = st.text_input("Email institucional")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            if not matricula or not email or not senha:
                st.warning("Preencha todos os campos.")
            else:
                resultado = supabase.table("estudantes").select("*").eq("matricula", matricula).execute()
                if resultado.data:
                    estudante = resultado.data[0]
                    if estudante.get("user_id"):
                        st.error("Essa matrícula já está vinculada a um usuário.")
                    else:
                        try:
                            auth_response = supabase.auth.sign_up({"email": email, "password": senha})
                            user_id = auth_response.user.id
                            supabase.table("estudantes").update({
                                "email": email,
                                "user_id": user_id
                            }).eq("matricula", matricula).execute()
                            st.success("Cadastro realizado com sucesso! Faça login para acessar.")
                        except Exception as e:
                            st.error(f"Erro ao cadastrar: {e}")
                else:
                    st.error("Matrícula não encontrada. Procure a instituição.")

    # CADASTRO DE EMPRESA
    elif tipo_usuario == "Empresa":
        nome = st.text_input("Nome da empresa")
        email = st.text_input("Email corporativo")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            if not nome or not email or not senha:
                st.warning("Preencha todos os campos.")
            else:
                try:
                    auth_response = supabase.auth.sign_up({"email": email, "password": senha})
                    user_id = auth_response.user.id
                    supabase.table("empresas").insert({
                        "nome": nome,
                        "email": email,
                        "user_id": user_id
                    }).execute()
                    st.success("Empresa cadastrada com sucesso! Faça login para continuar.")
                except Exception as e:
                    st.error(f"Erro ao cadastrar empresa: {e}")

# === LOGIN ===
elif choice == "Login":
    st.subheader("Login de Usuário")
    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        try:
            user = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            user_id = user.user.id

            # Verifica se é estudante
            estudante = supabase.table("estudantes").select("*").eq("user_id", user_id).execute()
            if estudante.data:
                nome = estudante.data[0]['nome']
                st.success("Login como Estudante realizado com sucesso!")
                st.write(f"Bem-vindo, {nome}")
                # Aqui você pode mostrar painel do estudante

            else:
                # Verifica se é empresa
                empresa = supabase.table("empresas").select("*").eq("user_id", user_id).execute()
                if empresa.data:
                    nome = empresa.data[0]['nome']
                    st.success("Login como Empresa realizado com sucesso!")
                    st.write(f"Bem-vindo, {nome}")
                    # Aqui você pode mostrar painel da empresa

                else:
                    st.warning("Usuário não identificado como estudante nem empresa.")

        except Exception as e:
            st.error(f"Erro no login: {e}")
