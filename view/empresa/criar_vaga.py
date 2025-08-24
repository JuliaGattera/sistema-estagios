import streamlit as st

def criar_vaga(supabase, user):
    st.subheader("Nova Vaga")

    titulo = st.text_input("Título da vaga")
    descricao = st.text_area("Descrição")
    quantidade = st.number_input("Quantidade de vagas", min_value=1, value=1)

    cursos_res = supabase.table("cursos").select("id, nome").execute()
    cursos = cursos_res.data
    curso_nomes = [c["nome"] for c in cursos]
    curso_selecionado = st.selectbox("Curso", curso_nomes)
    curso_id = next((c["id"] for c in cursos if c["nome"] == curso_selecionado), None)

    disciplinas_res = supabase.table("disciplinas").select("id, nome").eq("curso_id", curso_id).execute()
    disciplinas = disciplinas_res.data
    nomes_disciplinas = [d["nome"] for d in disciplinas]
    disciplinas_selecionadas = st.multiselect("Disciplinas exigidas", nomes_disciplinas)

    if st.button("Publicar Vaga"):
        if not titulo or not curso_id:
            st.warning("Preencha todos os campos obrigatórios.")
        else:
            try:
                vaga_insert = supabase.table("vagas").insert({
                    "empresa_id": user["id"],
                    "titulo": titulo,
                    "descricao": descricao,
                    "curso_id": curso_id,
                    "quantidade": quantidade
                }).execute()

                vaga_id = vaga_insert.data[0]["id"]

                for nome in disciplinas_selecionadas:
                    disciplina_id = next((d["id"] for d in disciplinas if d["nome"] == nome), None)
                    if disciplina_id:
                        supabase.table("vagas_disciplinas").insert({
                            "vaga_id": vaga_id,
                            "disciplina_id": disciplina_id
                        }).execute()

                st.success("Vaga publicada com sucesso!")

            except Exception as e:
                st.error(f"Erro ao criar vaga: {e}")

