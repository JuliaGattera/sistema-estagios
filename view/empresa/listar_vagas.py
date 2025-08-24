import streamlit as st

def listar_vagas(supabase, user):
    st.subheader("Minhas Vagas Ativas")
    vagas = supabase.table("vagas").select("*").eq("empresa_id", user["id"]).execute().data

    for vaga in vagas:
        st.markdown(f"### {vaga['titulo']}")
        st.markdown(f"{vaga.get('descricao', 'Sem descrição.')}")
        st.markdown(f"**Criada em:** {vaga.get('criada_em', '')}")
        st.markdown(f"**Quantidade de Vagas:** {vaga.get('quantidade', 1)}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Excluir vaga", key=f"excluir_{vaga['id']}"):
                try:
                    supabase.table("vagas").delete().eq("id", vaga["id"]).execute()
                    st.success("Vaga excluída com sucesso.")
                except Exception as e:
                    st.error(f"Erro ao excluir vaga: {e}")

