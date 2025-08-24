# view/admin/estudantes.py

import streamlit as st

def gerenciar_estudantes(supabase):
    st.subheader("Cadastrar Novo Estudante")

    nome = st.text_input("Nome do Estudante")
    email = st.text_input("Email")
    matricula = st.text_input("Matrícula")
    telefone = st.text_input("Telefone")

    cursos = supabase.table("cursos").select("*").execute().data
    nomes_cursos = [curso["nome"] for curso in cursos]
    curso_nome = st.selectbox("Curso", nomes_cursos)
    curso_id = next((c["id"] for c in cursos if c["nome"] == curso_nome), None)

    if st.button("Cadastrar Estudante"):
        if not all([nome, email, matricula, curso_id]):
            st.warning("Preencha todos os campos.")
        else:
            try:
                # Criar estudante
                estudante_insert = supabase.table("estudantes").insert({
                    "nome": nome,
                    "email": email,
                    "matricula": matricula,
                    "telefone": telefone,
                    "curso_id": curso_id
                }).execute()

                estudante_id = estudante_insert.data[0]["id"]

                # Inserir notas iniciais 0.00
                disciplinas_res = supabase.table("disciplinas").select("id").eq("curso_id", curso_id).execute()
                for disciplina in disciplinas_res.data:
                    supabase.table("notas_estudantes").insert({
                        "estudante_id": estudante_id,
                        "disciplina_id": disciplina["id"],
                        "nota": 0.00
                    }).execute()

                st.success("Estudante cadastrado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao cadastrar estudante: {e}")

    st.markdown("---")
    st.subheader("Editar Notas de Estudante Existente")

    # Selecionar estudante
    estudantes = supabase.table("estudantes").select("id, nome").execute().data
    nomes_estudantes = [e["nome"] for e in estudantes]
    estudante_nome = st.selectbox("Selecionar Estudante", nomes_estudantes)
    estudante_id = next((e["id"] for e in estudantes if e["nome"] == estudante_nome), None)

    if estudante_id:
        # Pegar notas + disciplinas
        query = supabase.table("notas_estudantes").select("id, nota, disciplina_id").eq("estudante_id", estudante_id).execute()
        notas = query.data

        for nota_entry in notas:
            disciplina = supabase.table("disciplinas").select("nome").eq("id", nota_entry["disciplina_id"]).execute().data
            nome_disciplina = disciplina[0]["nome"] if disciplina else "Desconhecida"

            nova_nota = st.number_input(f"Nota para {nome_disciplina}", min_value=0.0, max_value=10.0, step=0.1, value=nota_entry["nota"], key=nota_entry["id"])

            if st.button(f"Salvar nota de {nome_disciplina}", key=f"save_{nota_entry['id']}"):
                try:
                    supabase.table("notas_estudantes").update({
                        "nota": nova_nota
                    }).eq("id", nota_entry["id"]).execute()
                    st.success(f"Nota de {nome_disciplina} atualizada para {nova_nota}")
                except Exception as e:
                    st.error(f"Erro ao atualizar nota: {e}")
