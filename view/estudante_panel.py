# view/estudante_panel.py
import streamlit as st
from controller.vagas_controller import vagas_disponiveis_para_estudante

def show_estudante_panel(supabase, logout_func):
    user = st.session_state.user
    st.success(f"Login como Estudante realizado com sucesso! Bem-vindo, {user['nome']}")

    aba = st.radio("Menu", ["Meus Dados", "Vagas Disponíveis"])

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
