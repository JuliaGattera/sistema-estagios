import streamlit as st
from supabase import Client

def gerenciar_estudantes(supabase: Client):
    st.subheader("Cadastrar Novo Estudante")

    nome = st.text_input("Nome")
    email = st.text_input("Email")
    matricula = st.text_input("Matrícula")
    telefone = st.text_input("Telefone")

    cursos = supabase.table("cursos").select("id, nome").execute().data
    nomes_cursos = [c["nome"] for c in cursos]
    curso_selecionado = st.selectbox("Curso", nomes_cursos)
    curso_id = next((c["id"] for c in cursos if c["nome"] == curso_selecionado), None)

    if st.button("Cadastrar Estudante"):
        if not nome or not email or not matricula or not curso_id:
            st.warning("Preencha todos os campos obrigatórios.")
        else:
            try:
                estudante_insert = supabase.table("estudantes").insert({
                    "nome": nome,
                    "email": email,
                    "matricula": matricula,
                    "telefone": telefone,
                    "curso_id": curso_id
                }).execute()

                estudante_id = estudante_insert.data[0]["id"]

                # Inserir notas iniciais 0.00 para todas as disciplinas do curso
                disciplinas_res = supabase.table("disciplinas").select("id").eq("curso_id", curso_id).execute()
                disciplinas = disciplinas_res.data

                for disciplina in disciplinas:
                    supabase.table("notas_estudantes").insert({
                        "estudante_id": estudante_id,
                        "disciplina_id": disciplina["id"],
                        "nota": 0.00
                    }).execute()

                st.success("Estudante cadastrado com sucesso, com notas iniciais zeradas!")

            except Exception as e:
                st.error(f"Erro ao cadastrar estudante: {e}")
