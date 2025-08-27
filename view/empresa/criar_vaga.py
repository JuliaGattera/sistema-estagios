import streamlit as st
from datetime import datetime, timedelta
from controller.email_controller import notificar_estudante_por_email
from controller.vagas_controller import selecionar_estudantes_para_vaga

def criar_vaga(supabase, user):
    st.subheader("Nova Vaga")

    # Captura os inputs do usuário
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
            return

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

            prazo = datetime.utcnow() + timedelta(days=3)

            estudantes_ordenados = selecionar_estudantes_para_vaga(supabase, vaga_id, quantidade)

            enviados = 0
            for estudante_id, media in estudantes_ordenados:
                if enviados >= quantidade:
                    break

                supabase.table("log_vinculos_estudantes_vagas").insert({
                    "estudante_id": estudante_id,
                    "vaga_id": vaga_id,
                    "status": "notificado",
                    "prazo_resposta": prazo.isoformat()
                }).execute()

                sucesso, erro = notificar_estudante_por_email(
                    supabase,
                    estudante_id,
                    {"titulo": titulo, "descricao": descricao},
                    {"nome": user.get("nome", "Empresa")},
                    prazo,
                    st.secrets["email"]["user"],
                    st.secrets["email"]["password"]
                )

                if sucesso:
                    enviados += 1
                else:
                    st.error(f"Erro enviando email para estudante {estudante_id}: {erro}")

            st.success(f"E-mails enviados para {enviados} estudantes.")

        except Exception as e:
            st.error(f"Erro ao criar vaga e notificar estudantes: {e}")
