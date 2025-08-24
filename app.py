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

# Inicializa session_state para controle de usuário logado
if 'user' not in st.session_state:
    st.session_state.user = None
if 'user_type' not in st.session_state:
    st.session_state.user_type = None

##########################################
###função que faz a triagem das vagas que serão exibidas para o aluno:
def vagas_disponiveis_para_estudante(supabase: Client, user_id: str, nota_minima=7.0):
    # 1. Buscar estudante e seu curso
    estudante_res = supabase.table("estudantes").select("id, curso_id").eq("user_id", user_id).execute()
    if not estudante_res.data:
        return []

    estudante = estudante_res.data[0]
    estudante_id = estudante["id"]
    curso_id = estudante["curso_id"]

    # 2. Buscar vagas do curso
    vagas_res = supabase.table("vagas").select("id, titulo, descricao").eq("curso_id", curso_id).execute()
    vagas = vagas_res.data

    vagas_filtradas = []

    for vaga in vagas:
        vaga_id = vaga["id"]
        
        # 3. Buscar disciplinas exigidas pela vaga
        vagas_disciplinas_res = supabase.table("vagas_disciplinas").select("disciplina_id").eq("vaga_id", vaga_id).execute()
        disciplinas_ids = [d["disciplina_id"] for d in vagas_disciplinas_res.data]

        # 4. Buscar notas do estudante nessas disciplinas
        notas_res = supabase.table("notas_estudantes").select("disciplina_id, nota").eq("estudante_id", estudante_id).in_("disciplina_id", disciplinas_ids).execute()
        notas = notas_res.data

        # 5. Verificar se o estudante tem nota mínima em todas as disciplinas exigidas
        # Se faltar alguma disciplina ou nota for menor que a mínima, não passa
        notas_dict = {n["disciplina_id"]: n["nota"] for n in notas}
        atende = all(notas_dict.get(did, 0) >= nota_minima for did in disciplinas_ids)

        if atende:
            vagas_filtradas.append(vaga)

    return vagas_filtradas

###########################################
def logout():
    st.session_state.user = None
    st.session_state.user_type = None
    st.experimental_rerun()

# Se usuário não está logado, mostra menu Login/Cadastro
if st.session_state.user is None:

    menu = ["Login", "Cadastro"]
    choice = st.sidebar.selectbox("Menu", menu)

    # === CADASTRO ===
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
                    st.session_state.user = estudante.data[0]
                    st.session_state.user_type = 'estudante'
                    st.experimental_rerun()

                else:
                    # Verifica se é empresa
                    empresa = supabase.table("empresas").select("*").eq("user_id", user_id).execute()
                    if empresa.data:
                        st.session_state.user = empresa.data[0]
                        st.session_state.user_type = 'empresa'
                        st.experimental_rerun()
                    else:
                        st.warning("Usuário não identificado como estudante nem empresa.")

            except Exception as e:
                st.error(f"Erro no login: {e}")

# Se usuário está logado, mostra painel e botão logout
else:
    if st.session_state.user_type == 'estudante':
        user = st.session_state.user
        st.success(f"Login como Estudante realizado com sucesso! Bem-vindo, {user['nome']}")
        aba = st.radio("Menu", ["Meus Dados", "Vagas Disponíveis"])

        if st.button("Logout"):
            logout()

        if aba == "Meus Dados":
            st.text_input("Email", value=user.get("email", ""), disabled=True)
            novo_telefone = st.text_input("Telefone", value=user.get("telefone", ""))
            

            if st.button("Atualizar dados"):
                try:
                    supabase.table("estudantes").update({
                        "email": novo_email,
                        "telefone": novo_telefone
                    }).eq("user_id", user['user_id']).execute()
                    st.success("Dados atualizados com sucesso!")
                except Exception as e:
                    st.error(f"Erro ao atualizar dados: {e}")

        elif aba == "Vagas Disponíveis":
            user = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            user_id = user.user.id
            vagas_filtradas = vagas_disponiveis_para_estudante(supabase, user_id)
        
            if vagas_filtradas:
                for vaga in vagas_filtradas:
                    st.markdown(f"### {vaga['titulo']}")
                    st.markdown(f"{vaga.get('descricao', 'Sem descrição.')}")
                    if st.button(f"Candidatar-se à vaga: {vaga['titulo']}", key=vaga['id']):
                        try:
                            supabase.table("log_vinculos_estudantes_vagas").insert({
                                "estudante_id": user['id'],
                                "vaga_id": vaga['id'],
                                "status": "notificado"
                            }).execute()
                            st.success("Candidatura registrada com sucesso!")
                        except Exception as e:
                            st.error(f"Erro ao se candidatar: {e}")
            else:
                st.info("Nenhuma vaga disponível para seu curso que atenda aos seus critérios de nota.")

    elif st.session_state.user_type == 'empresa':
        user = st.session_state.user
        st.success(f"Login como Empresa realizado com sucesso! Bem-vindo, {user['nome']}")
        if st.button("Logout"):
            logout()
        # Aqui você pode montar o painel da empresa

