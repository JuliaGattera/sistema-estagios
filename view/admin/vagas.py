# view/admin/vagas.py

import streamlit as st
from supabase import Client

def gerenciar_vagas_admin(supabase: Client):
    st.subheader("Gerenciar Vagas e Estudantes Vinculados")

    vagas = supabase.table("vagas").select("id, titulo, descricao, quantidade").execute().data

    for vaga in vagas:
        st.markdown("----")
        st.markdown(f"### 🧾 {vaga['titulo']}")
        st.markdown(f"**Descrição:** {vaga.get('descricao', 'Sem descrição.')}")
        st.markdown(f"**Quantidade total de vagas:** {vaga['quantidade']}")

        # Buscar vínculos dos estudantes
        log_vinculos = supabase.table("log_vinculos_estudantes_vagas") \
            .select("id, estudante_id, status") \
            .eq("vaga_id", vaga["id"]) \
            .execute().data

        # Contar quantos foram contratados
        contratados = [v for v in log_vinculos if v["status"] == "contratado"]
        num_contratados = len(contratados)

        # Determinar status da vaga
        status_vaga = "✅ Fechada" if num_contratados >= vaga["quantidade"] else "🟢 Aberta"
        st.markdown(f"**Status da Vaga:** {status_vaga}")
        st.markdown(f"**Contratados:** {num_contratados} / {vaga['quantidade']}")

        if not log_vinculos:
            st.info("Nenhum estudante vinculado a esta vaga.")
        else:
            st.markdown("**Estudantes vinculados:**")
            for vinculo in log_vinculos:
                estudante = supabase.table("estudantes") \
                    .select("nome, email") \
                    .eq("id", vinculo["estudante_id"]) \
                    .execute().data

                if estudante:
                    nome = estudante[0]["nome"]
                    email = estudante[0]["email"]
                    status = vinculo["status"]
                    st.markdown(f"- 👤 **{nome}** ({email}) → Status: `{status}`")
