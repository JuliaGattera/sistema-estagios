import streamlit as st

def gerenciar_estudantes(supabase):
    st.subheader("Estudantes Cadastrados")

    estudantes = supabase.table("estudantes").select("nome, email, matricula, telefone").execute().data
    if not estudantes:
        st.info("Nenhum estudante cadastrado ainda.")
        return

    for est in estudantes:
        st.markdown(f"""
        **Nome:** {est['nome']}  
        **Email:** {est['email']}  
        **Matrícula:** {est['matricula']}  
        **Telefone:** {est.get('telefone', 'Não informado')}
        """)
        st.divider()

