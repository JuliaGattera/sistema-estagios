import streamlit as st
from datetime import datetime, timezone
def show_estudante_panel(supabase, logout_func):
    user = st.session_state.user
    st.success(f"Login como Estudante realizado com sucesso! Bem-vindo, {user['nome']}")

    aba = st.radio("Menu", ["Meus Dados", "Vagas Notificadas"])

    if st.button("Logout"):
        logout_func()

    # === ABA 1: MEUS DADOS ===
    if aba == "Meus Dados":
        st.text_input("Email", value=user.get("email", ""), disabled=True)
        novo_telefone = st.text_input("Telefone", value=user.get("telefone", ""))

        if st.button("Atualizar dados"):
            try:
                supabase.table("estudantes").update({
                    "telefone": novo_telefone
                }).eq("user_id", user['user_id']).execute()
                st.success("Dados atualizados com sucesso!")
            except Exception as e:
                st.error(f"Erro ao atualizar dados: {e}")

    # === ABA 2: VAGAS NOTIFICADAS ===
    elif aba == "Vagas Notificadas":
        estudante_id = user["id"]
        vinculos_res = supabase.table("log_vinculos_estudantes_vagas")\
            .select("id, vaga_id, prazo_resposta")\
            .eq("estudante_id", estudante_id)\
            .eq("status", "notificado")\
            .execute()

        vinculos = vinculos_res.data

        if not vinculos:
            st.info("Você não foi notificado para nenhuma vaga até o momento.")
        else:
            for vinculo in vinculos:
                prazo_str = vinculo.get("prazo_resposta")
                if prazo_str:
                    prazo = datetime.fromisoformat(prazo_str.replace("Z", "+00:00"))
                    if datetime.now(timezone.utc) > prazo:
                        continue  # Ignora vaga expirada
                else:
                    continue  # Sem prazo, ignora

                # Buscar detalhes da vaga
                vaga_id = vinculo["vaga_id"]
                vaga_res = supabase.table("vagas")\
                    .select("titulo, descricao")\
                    .eq("id", vaga_id).execute()

                if not vaga_res.data:
                    continue

                vaga = vaga_res.data[0]

                st.markdown(f"### 📌 {vaga['titulo']}")
                st.markdown(vaga.get("descricao", "Sem descrição disponível."))
                st.markdown(f"📅 Prazo para resposta: `{prazo.strftime('%d/%m/%Y %H:%M UTC')}`")
                #
                if st.button(f"Desistir desta vaga", key=f"desistir_{vaga_id}"):
                    try:
                        supabase.table("log_vinculos_estudantes_vagas").update({
                            "status": "desistente",
                            "data_vinculo": datetime.utcnow().isoformat()
                        }).eq("id", vinculo["id"]).execute()
                        st.success("Você desistiu da vaga.")
                        from controller.vagas_controller import chamar_proximos_estudantes_disponiveisv3
                        chamar_proximos_estudantes_disponiveisv3(supabase, vaga['id'],1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao desistir da vaga: {e}")

