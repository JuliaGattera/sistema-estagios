import streamlit as st
from datetime import datetime, timedelta
from controller.email_controller import notificar_estudante_por_email

def criar_vaga(supabase, user):
    st.subheader("Nova Vaga")

    # ... seu código normal para pegar inputs e criar vaga ...

    if st.button("Publicar Vaga"):
        # Validação e inserção da vaga + disciplinas

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

            # Definir prazo para resposta
            prazo = datetime.utcnow() + timedelta(days=3)

            # Lógica para pegar estudantes com maiores médias (igual antes)...

            # Exemplo simplificado:
            estudantes_ordenados = [...]  # sua lista já calculada

            enviados = 0
            for estudante_id, media in estudantes_ordenados:
                if enviados >= quantidade:
                    break

                # Inserir no log
                supabase.table("log_vinculos_estudantes_vagas").insert({
                    "estudante_id": estudante_id,
                    "vaga_id": vaga_id,
                    "status": "notificado",
                    "prazo_resposta": prazo.isoformat()
                }).execute()

                # Chamar função do controller para notificar
                sucesso, erro = notificar_estudante_por_email(
                    supabase,
                    estudante_id,
                    {"titulo": titulo, "descricao": descricao},
                    {"nome": user["nome"]},
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
