import streamlit as st

def candidatos_vagas(supabase, user):
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

