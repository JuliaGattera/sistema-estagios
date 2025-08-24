import streamlit as st

def gerenciar_cursos(supabase):
    st.subheader("Cadastro de Cursos")

    nome_curso = st.text_input("Nome do Curso")

    if st.button("Adicionar Curso"):
        if nome_curso.strip() == "":
            st.warning("Informe o nome do curso.")
        else:
            try:
                supabase.table("cursos").insert({"nome": nome_curso}).execute()
                st.success(f"Curso '{nome_curso}' adicionado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao adicionar curso: {e}")

    st.divider()

    st.subheader("Cursos Cadastrados")
    cursos = supabase.table("cursos").select("*").execute().data
    for curso in cursos:
        st.markdown(f"- {curso['nome']}")

