import streamlit as st
from supabase import Client
from datetime import datetime

def show_empresa_panel(supabase: Client):
    user = st.session_state.user
    st.title("Painel da Empresa")
    st.success(f"Bem-vindo(a), {user['nome']}")

    aba = st.radio("Menu da Empresa", ["Cadastrar Vaga", "Minhas Vagas", "Candidatos às Vagas"])

    # === CADASTRAR NOVA VAGA ===
    if aba == "Cadastrar Vaga":
        st.subheader("Cadastrar Nova Vaga")

        titulo = st.text_input("Título da Vaga")
        descricao = st.text_area("Descrição da Vaga")
        quantidade = st.number_input("Quantidade de Vagas", min_value=1, step=1)
        cursos = supabase.table("cursos").select("*").execute().data
        curso_opcoes = {c["nome"]: c["id"] for c in cursos}
        curso_nome = st.selectbox("Curso relacionado", list(curso_opcoes.keys()))
        curso_id = curso_opcoes[curso_nome]

        # Seleção de disciplinas
        disciplinas = supabase.table("disciplinas").select("*").eq("curso_id", curso_id).execute().data
        disciplina_opcoes = {d["nome"]: d["id"] for d in disciplinas}
        disciplinas_escolhidas = st.multiselect("Disciplinas exigidas", list(disciplina_opcoes.keys()))

        if st.button("Publicar Vaga"):
            try:
                nova_vaga = supabase.table("vagas").insert({
                    "empresa_id": user["id"],
                    "titulo": titulo,
                    "descricao": descricao,
                    "curso_id": curso_id,
                    "quantidade": quantidade
                }).execute()
                vaga_id = nova_vaga.data[0]["id"]

                for nome in disciplinas_escolhidas:
                    supabase.table("vagas_disciplinas").insert({
                        "vaga_id": vaga_id,
                        "disciplina_id": disciplina_opcoes[nome]
                    }).execute()

                st.success("Vaga cadastrada com sucesso!")
            except Exception as e:
                st.error(f"Erro ao cadastrar vaga: {e}")

    # === EXIBIR VAGAS DA EMPRESA ===
    elif aba == "Minhas Vagas":
        st.subheader("Minhas Vagas")
        vagas = supabase.table("vagas").select("*").eq("empresa_id", user["id"]).order("criada_em", desc=True).execute().data

        if not vagas:
            st.info("Nenhuma vaga cadastrada ainda.")
        else:
            for vaga in vagas:
                st.markdown(f"### {vaga['titulo']}")
                st.markdown(f"**Descrição:** {vaga.get('descricao', 'Sem descrição')}")
                st.markdown(f"**Quantidade:** {vaga.get('quantidade', 1)}")

                # Buscar quantidade de estudantes contratados para essa vaga
                log = supabase.table("log_vinculos_estudantes_vagas").select("id").eq("vaga_id", vaga["id"]).eq("status", "contratado").execute()
                num_contratados = len(log.data)
                st.markdown(f"**Contratados:** {num_contratados}")

                if st.button(f"Marcar como preenchida (encerrar)", key=f"fechar_{vaga['id']}"):
                    try:
                        supabase.table("vagas").update({"quantidade": 0}).eq("id", vaga["id"]).execute()
                        st.success("Vaga marcada como preenchida.")
                    except Exception as e:
                        st.error(f"Erro ao atualizar vaga: {e}")

                if st.button(f"Excluir vaga", key=f"excluir_{vaga['id']}"):
                    try:
                        supabase.table("vagas").delete().eq("id", vaga["id"]).execute()
                        st.success("Vaga excluída.")
                    except Exception as e:
                        st.error(f"Erro ao excluir vaga: {e}")

                st.markdown("---")

    # === VER CANDIDATOS ÀS VAGAS ===
    elif aba == "Candidatos às Vagas":
        st.subheader("Candidatos às Minhas Vagas")

        vagas = supabase.table("vagas").select("*").eq("empresa_id", user["id"]).execute().data

        if not vagas:
            st.info("Você ainda não cadastrou vagas.")
        else:
            for vaga in vagas:
                st.markdown(f"## {vaga['titulo']}")
                vinculos = supabase.table("log_vinculos_estudantes_vagas").select("*").eq("vaga_id", vaga["id"]).execute().data

                if not vinculos:
                    st.info("Nenhum candidato ainda.")
                else:
                    for vinculo in vinculos:
                        estudante_id = vinculo["estudante_id"]
                        estudante = supabase.table("estudantes").select("*").eq("id", estudante_id).execute().data[0]
                        st.markdown(f"**Nome:** {estudante['nome']} - **Email:** {estudante['email']}")
                        st.markdown(f"**Status:** {vinculo['status']}")

                        if vinculo["status"] != "contratado":
                            if st.button("Contratar", key=f"contratar_{vinculo['id']}"):
                                try:
                                    supabase.table("log_vinculos_estudantes_vagas").update({
                                        "status": "contratado",
                                        "data_vinculo": datetime.utcnow().isoformat()
                                    }).eq("id", vinculo["id"]).execute()
                                    st.success("Estudante contratado com sucesso.")
                                except Exception as e:
                                    st.error(f"Erro ao contratar: {e}")
                        st.markdown("---")
