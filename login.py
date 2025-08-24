import streamlit as st
from supabase import Client

def show_login_screen(supabase: Client):
    menu = ["Login", "Cadastro"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login de Usuário")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                user_id = user.user.id

                if email == "admin@admin.com":
                    st.session_state.user = {"email": email}
                    st.session_state.user_type = 'admin'
                    st.experimental_rerun()

                estudante = supabase.table("estudantes").select("*").eq("user_id", user_id).execute()
                if estudante.data:
                    st.session_state.user = estudante.data[0]
                    st.session_state.user_type = 'estudante'
                    st.experimental_rerun()

                empresa = supabase.table("empresas").select("*").eq("user_id", user_id).execute()
                if empresa.data:
                    st.session_state.user = empresa.data[0]
                    st.session_state.user_type = 'empresa'
                    st.experimental_rerun()

                st.warning("Usuário não identificado.")

            except Exception as e:
                st.error(f"Erro no login: {e}")

    elif choice == "Cadastro":
        st.subheader("Cadastro de Usuário")
        st.info("Cadastro será implementado em breve.")
