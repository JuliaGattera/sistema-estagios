# view/empresa_panel.py

import streamlit as st
from supabase import Client
from datetime import datetime

def show_empresa_panel(supabase: Client, logout_fn):
    user = st.session_state.user

    st.success(f"Login como Empresa realizado com sucesso! Bem-vindo, {user['nome']}")

    # Botão de logout
    if st.button("Logout"):
        logout_fn()

    aba = st.radio("Menu da Empresa", [
        "Criar Nova Vaga",
        "Minhas Vagas",
        "Candidatos às Vagas"
    ])

    # 1. Criar Nova Vaga
    if aba == "Criar Nova Vaga":
        st.subheader("Nova Vaga")

        titulo = st.text_input("Título da vaga")
        descricao = st.text_area("Descrição")
        quantidade = st.number_input("Quantidade de vagas", min_value=1, value=1)

        cursos_res = supabase.table("cursos").select("id, nome").execute()
        cursos = cursos_res.data
        curso_nomes = [c["nome"] for c in cursos]
        curso_selecionado = st.selectbox("Curso", curso_nomes)
        curso_id = next((c["id"] for c in cursos if c["nome"] == curso_selecionado), None)

        # Disciplinas vinculadas ao curso
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

    # 2. Minhas Vagas
    elif aba == "Minhas Vagas":
        st.subheader("Minhas Vagas Ativas")
        vagas = supabase.table("vagas").select("*").eq("empresa_id", user["id"]).execute().data

        for vaga in vagas:
            st.markdown(f"### {vaga['titulo']}")
            st.markdown(f"{vaga.get('descricao', 'Sem descrição.')}")
            st.markdown(f"**Criada em:** {vaga.get('criada_em', '')}")
            st.markdown(f"**Quantidade de Vagas:** {vaga.get('quantidade', 1)}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button("Marcar como preenchida", key=f"preenchida_{vaga['id']}"):
                    try:
                        supabase.table("vagas").update({"quantidade": 0}).eq("id", vaga["id"]).execute()
                        st.success("Vaga marcada como preenchida.")
                    except Exception as e:
                        st.error(f"Erro ao atualizar vaga: {e}")

            with col2:
                if st.button("Excluir vaga", key=f"excluir_{vaga['id']}"):
                    try:
                        supabase.table("vagas").delete().eq("id", vaga["id"]).execute()
                        st.success("Vaga excluída com sucesso.")
                    except Exception as e:
                        st.error(f"Erro ao excluir vaga: {e}")

    # 3. Ver candidatos às vagas
    elif aba == "Candidatos às Vagas":
        st.subheader("Candidatos às Suas Vagas")

        vagas = supabase.table("vagas").select("id, titulo").eq("empresa_id", user["id"]).execute().data

        for vaga in vagas:
            st.markdown(f"### Vaga: {vaga['titulo']}")
            log = supabase.table("log_vinculos_estudantes_vagas").select("*, estudante_id").eq("vaga_id", vaga["id"]).execute().data

            for entrada in log:
                estudante_id = entrada["estudante_id"]
                estudante_info = supabase.table("estudantes").select("nome, email").eq("id", estudante_id).execute().data
                if estudante_info:
                    nome = estudante_info[0]["nome"]
                    email = estudante_info[0]["email"]
                    status = entrada["status"]
                    st.markdown(f"- **{nome}** ({email}) - Status: **{status}**")

                    if status != "contratado":
                        if st.button(f"Marcar como contratado: {nome}", key=f"contratar_{entrada['id']}"):
                            try:
                                supabase.table("log_vinculos_estudantes_vagas").update({"status": "contratado"}).eq("id", entrada["id"]).execute()
                                st.success(f"{nome} marcado como contratado.")
                            except Exception as e:
                                st.error(f"Erro ao atualizar status: {e}")
