import streamlit as st

def show_login_screen(supabase):
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

    elif choice == "Login":
        st.subheader("Login de Usuário")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar"):
            try:
                user = supabase.auth.sign_in_with_password({"email": email, "password": senha})
                user_id = user.user.id

                # Verificar o tipo de usuário
                if email == "admin@admin.com":
                    st.session_state.user = {"email": email}
                    st.session_state.user_type = 'admin'
                
                else:
                    estudante = supabase.table("estudantes").select("*").eq("user_id", user_id).execute()
                    if estudante.data:
                        st.session_state.user = estudante.data[0]
                        st.session_state.user_type = 'estudante'
                    else:
                        empresa = supabase.table("empresas").select("*").eq("user_id", user_id).execute()
                        if empresa.data:
                            st.session_state.user = empresa.data[0]
                            st.session_state.user_type = 'empresa'
                        else:
                            st.warning("Usuário não identificado como estudante, empresa ou admin.")
                            return

                # Marcar que o usuário está logado na sessão
                st.session_state.logged_in = True

                # Evitar 'st.experimental_rerun()' aqui diretamente
                # Navegar ou redirecionar para outra página
                if st.session_state.user_type == 'admin':
                    # Exemplo de navegação para o painel do administrador
                    st.write("Bem-vindo, Admin!")
                    # Aqui poderia haver o redirecionamento para uma outra página com o painel admin
                elif st.session_state.user_type == 'estudante':
                    # Exemplo de navegação para o painel do estudante
                    st.write("Bem-vindo, Estudante!")
                else:
                    st.write("Bem-vindo, Empresa!")

            except Exception as e:
                st.error(f"Erro no login: {e}")

    # Se o usuário estiver logado, redirecionar para a próxima tela (como exemplo)
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        # Remover o 'st.experimental_rerun()' aqui
        # Com isso, a página não será recarregada automaticamente, evitando o segundo clique
        st.write("Você está logado com sucesso!")

