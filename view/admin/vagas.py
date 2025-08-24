import streamlit as st

def gerenciar_vagas(supabase):
    st.subheader("Todas as Vagas Cadastradas")

    vagas = supabase.table("vagas").select("id, titulo, descricao, quantidade, criada_em").execute().data
    if not vagas:
        st.info("Nenhuma vaga cadastrada.")
        return

    for vaga in vagas:
        st.markdown(f"""
        ### {vaga['titulo']}
        {vaga.get('descricao', 'Sem descrição.')}
        - Quantidade: {vaga.get('quantidade')}
        - Criada em: {vaga.get('criada_em', '').split('T')[0]}
        """)
        st.divider()

