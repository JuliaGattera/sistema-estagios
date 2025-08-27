import streamlit as st
from controller.vagas_controller import vagas_disponiveis_para_estudante
from datetime import datetime

def show_estudante_panel(supabase, logout_func):
    user = st.session_state.user
    st.success(f"Login como Estudante realizado com sucesso! Bem-vindo, {user['nome']}")

    aba = st.radio("Menu", ["Meus Dados", "Vagas Disponíveis", "Vagas Notificadas"])

    if st.button("Logout"):
        logout_func()

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

    elif aba == "Vagas Disponíveis":
        user_id = user.get("user_id")
        vagas_filtradas = vagas_disponiveis_para_estudante(supabase, user_id)

        if vagas_filtradas:
            for vaga in vagas_filtradas:
                st.markdown(f"### {vaga['titulo']}")
                st.markdown(f"{vaga.get('descricao', 'Sem descrição.')}")
                if st.button(f"Candidatar-se à vaga: {vaga['titulo']}", key=vaga['id']):
                    try:
                        supabase.table("log_vinculos_estudantes_vagas").insert({
                            "estudante_id": user['id'],
                            "vaga_id": vaga['id'],
                            "status": "notificado"
                        }).execute()
                        st.success("Candidatura registrada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao se candidatar: {e}")
        else:
            st.info("Nenhuma vaga disponível para seu curso que atenda aos seus critérios de nota.")

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
                    if datetime.utcnow() > prazo:
                        continue  # prazo expirado
                else:
                    continue  # sem prazo, ignora

                vaga_id = vinculo["vaga_id"]
                vaga_res = supabase.table("vagas")\
                    .select("titulo, descricao")\
                    .eq("id", vaga_id).execute()

                if not vaga_res.data:
                    continue

                vaga = vaga_res.data[0]

                st.markdown(f"### {vaga['titulo']}")
                st.markdown(vaga.get("descricao", "Sem descrição disponível."))
                st.markdown(f"📅 Prazo para resposta: `{prazo.strftime('%d/%m/%Y %H:%M UTC')}`")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Recusar vaga: {vaga['titulo']}", key=f"recusar_{vaga_id}"):
                        try:
                            supabase.table("log_vinculos_estudantes_vagas").update({
                                "status": "recusado",
                                "data_atualizacao": datetime.utcnow().isoformat()
                            }).eq("id", vinculo["id"]).execute()
                            st.success("Vaga recusada com sucesso.")
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Erro ao recusar vaga: {e}")
                with col2:
                    st.write("")  # Espaço vazio ou botão futuro
