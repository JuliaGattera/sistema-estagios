import os
import streamlit as st
from supabase import create_client, Client

# Variáveis de ambiente
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

st.set_page_config(page_title="Sistema de Estágios", layout="centered")
st.title("Sistema de Estágios")

menu = ["Login", "Cadastro"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Cadastro":
    st.subheader("Cadastro de Usuário")
    tipo_usuario = st.selectbox("Tipo de usuário", ["Estudante", "Empresa"])

    if tipo_usuario == "Estudante":
        matricula = st.text_input("Matrícula")
        email = st.text_input("Email institucional")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            if not matricula or not email or not senha:
                st.warning("Preencha todos os campos.")
            else:
                # Verifica se a matrícula já existe no banco
                resultado = supabase.table("estudantes").select("*").eq("matricula", matricula).execute()
                if resultado.data:
                    estudante = resultado.data[0]
                    if estudante.get("user_id"):
                        st.error("Essa matrícula já está vinculada a um usuário.")
                    else:
                        try:
                            # Cria o usuário no Supabase Auth
                            auth_response = supabase.auth.sign_up({"email": email, "password": senha})
                            user_id = auth_response.user.id

                            # Atualiza o registro do estudante com email e user_id
                            supabase.table("estudantes").update({
                                "email": email,
                                "user_id": user_id
                            }).eq("matricula", matricula).execute()

                            st.success("Cadastro realizado com sucesso! Faça login para acessar.")
                        except Exception as e:
                            st.error(f"Erro ao cadastrar: {e}")
                else:
                    st.error("Matrícula não encontrada. Procure a instituição.")

    elif tipo_usuario == "Empresa":
        nome = st.text_input("Nome da empresa")
        email = st.text_input("Email corporativo")
        senha = st.text_input("Senha", type="password")

        if st.button("Cadastrar"):
            if not nome or not email or not senha:
                st.warning("Preencha todos os campos.")
            else:
                try:
                    # Cria usuário Auth
                    auth_response = supabase.auth.sign_up({"email": email, "password": senha})
                    user_id = auth_response.user.id

                    # Cadastra a empresa no banco
                    supabase.table("empresas").insert({
                        "nome": nome,
                        "email": email,
                        "user_id": user_id
                    }).execute()

                    st.success("Empresa cadastrada com sucesso! Faça login para continuar.")
                except Exception as e:
                    st.error(f"Erro ao cadastrar empresa: {e}")
