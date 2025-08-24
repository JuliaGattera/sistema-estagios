# view/admin/estudantes.py

import streamlit as st

def gerenciar_estudantes(supabase):
    st.subheader("Gerenciar Estudantes")

    # Buscar cursos disponíveis
    cursos_res = supabase.table("cursos").select("id, nome").execute()
    cursos = cursos_res.data
    cursos_dict = {c["nome"]: c["id"] for c in cursos}

    if not cursos:
        st.warning("Cadastre um curso antes de adicionar estudantes.")
        return

    # Formulário para adicionar novo estudante
    with st.expander("➕ Adicionar Estudante"):
        nome = st.text_input("Nome do estudante")
        matricula = st.text_input("Matrícula")
        email = st.text_input("Email")
        telefone = st.text_input("Telefone")
        curso_nome = st.selectbox("Curso", list(cursos_dict.keys()))

        if st.button("Adicionar Estudante"):
            if not nome or not matricula or not email or not curso_nome:
                st.warning("Preencha todos os campos obrigatórios.")
            else:
                curso_id = cursos_dict[curso_nome]

                # Inserir o estudante
                try:
                    novo_estudante = supabase.table("estudantes").insert({
                        "nome": nome,
                        "matricula": matricula,
                        "email": email,
                        "telefone": telefone,
                        "curso_id": curso_id
                    }).execute().data[0]

                    estudante_id = novo_estudante["id"]

                    # Buscar disciplinas do curso
                    disciplinas_res = supabase.table("disciplinas").select("id").eq("curso_id", curso_id).execute()
                    disciplinas = disciplinas_res.data

                    # Inserir notas zeradas para as disciplinas
                    for disciplina in disciplinas:
                        supabase.table("notas_estudantes").insert({
                            "estudante_id": estudante_id,
                            "disciplina_id": disciplina["id"],
                            "nota": 0.0
                        }).execute()

                    st.success("Estudante cadastrado com sucesso!")

                except Exception as e:
                    st.error(f"Erro ao adicionar estudante: {e}")

    # Listagem de estudantes cadastrados
    st.divider()
    st.subheader("Estudantes Cadastrados")

    estudantes = supabase.table("estudantes").select("nome, matricula, email").execute().data

    if estudantes:
        for est in estudantes:
            st.markdown(f"**{est['nome']}**  \nMatrícula: {est['matricula']}  \nEmail: {est['email']}")
            st.markdown("---")
    else:
        st.info("Nenhum estudante cadastrado.")
