import streamlit as st

def gerenciar_disciplinas(supabase):
    st.subheader("Gerenciar Disciplinas")

    cursos = supabase.table("cursos").select("id, nome").execute().data
    if not cursos:
        st.warning("Cadastre cursos antes de inserir disciplinas.")
        return

    curso_nomes = [c["nome"] for c in cursos]
    curso_selecionado = st.selectbox("Curso", curso_nomes)
    curso_id = next(c["id"] for c in cursos if c["nome"] == curso_selecionado)

    nome_disciplina = st.text_input("Nome da Disciplina")

    if st.button("Adicionar Disciplina"):
        if not nome_disciplina.strip():
            st.warning("Informe o nome da disciplina.")
        else:
            try:
                supabase.table("disciplinas").insert({
                    "nome": nome_disciplina,
                    "curso_id": curso_id
                }).execute()
                st.success("Disciplina adicionada com sucesso!")
            except Exception as e:
                st.error(f"Erro ao adicionar disciplina: {e}")

    st.divider()

    st.subheader("Disciplinas do Curso")
    disciplinas = supabase.table("disciplinas").select("*").eq("curso_id", curso_id).execute().data
    for d in disciplinas:
        st.markdown(f"- {d['nome']}")

