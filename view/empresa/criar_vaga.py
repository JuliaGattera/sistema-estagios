import streamlit as st
from datetime import datetime, timedelta
from controller.email_controller import notificar_estudante_por_email
from controller.vagas_controller import selecionar_estudantes_para_vaga

def criar_vaga(supabase, user):
    st.subheader("Nova Vaga")

    # 🔄 Verifica se precisa resetar os campos após publicação
    if st.session_state.get("vaga_publicada", False):
        st.session_state["titulo"] = ""
        st.session_state["descricao"] = ""
        st.session_state["quantidade"] = 1
        st.session_state["curso"] = ""
        st.session_state["disciplinas"] = []
        st.session_state["vaga_publicada"] = False

    # Captura os inputs do usuário com chaves únicas
    titulo = st.text_input("Título da vaga", key="titulo")
    descricao = st.text_area("Descrição", key="descricao")
    quantidade = st.number_input("Quantidade de vagas", min_value=1, value=1, key="quantidade")

    cursos_res = supabase.table("cursos").select("id, nome").execute()
    cursos = cursos_res.data
    curso_nomes = [c["nome"] for c in cursos]

    # Define curso padrão se não estiver definido ainda
    if "curso" not in st.session_state or not st.session_state["curso"]:
        st.session_state["curso"] = curso_nomes[0] if curso_nomes else ""

    curso_selecionado = st.selectbox("Curso", curso_nomes, key="curso")
    curso_id = next((c["id"] for c in cursos if c["nome"] == curso_selecionado), None)

    disciplinas_res = supabase.table("disciplinas").select("id, nome").eq("curso_id", curso_id).execute()
    disciplinas = disciplinas_res.data
    nomes_disciplinas = [d["nome"] for d in disciplinas]

    if "disciplinas" not in st.session_state:
        st.session_state["disciplinas"] = []

    disciplinas_selecionadas = st.multiselect("Disciplinas exigidas", nomes_disciplinas, key="disciplinas")

    if st.button("Publicar Vaga"):
        if not titulo or not curso_id:
            st.warning("Preencha todos os campos obrigatórios.")
            return

        try:
            # Verificar se já existe vaga com mesmos dados
            vaga_existente = supabase.table("vagas") \
                .select("id") \
                .eq("empresa_id", user["id"]) \
                .eq("titulo", titulo) \
                .eq("descricao", descricao) \
                .eq("curso_id", curso_id) \
                .execute()

            if vaga_existente.data:
                st.warning("Já existe uma vaga com os mesmos dados. Evite duplicações.")
                return

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

            prazo = datetime.utcnow() + timedelta(days=3)
            estudantes_ordenados = selecionar_estudantes_para_vaga(supabase, vaga_id, quantidade * 2)

            enviados = 0
            for estudante_id, media in estudantes_ordenados:
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
                    {"nome": user["nome"], "email": user["email"]},
                    prazo
                )

                if sucesso:
                    enviados += 1
                else:
                    st.error(f"Erro enviando email para estudante {estudante_id}: {erro}")

            st.success("Vaga publicada com sucesso!")
            st.success(f"E-mails enviados para {enviados} estudantes.")

            # 🔄 Define flag para resetar campos e força rerun
            st.session_state["vaga_publicada"] = True
            st.experimental_rerun()

        except Exception as e:
            st.error(f"Erro ao criar vaga e notificar estudantes: {e}")
