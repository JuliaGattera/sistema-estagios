import streamlit as st

def gerenciar_empresas(supabase):
    st.subheader("Empresas Cadastradas")

    empresas = supabase.table("empresas").select("nome, email, area").execute().data
    if not empresas:
        st.info("Nenhuma empresa cadastrada ainda.")
        return

    for emp in empresas:
        st.markdown(f"""
        **Nome:** {emp['nome']}  
        **Email:** {emp['email']}  
        **Área:** {emp.get('area', 'Não informada')}
        """)
        st.divider()

