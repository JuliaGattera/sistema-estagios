import streamlit as st
from datetime import datetime, timezone, timedelta


def listar_vagas_com_candidatos(supabase, user):
    st.subheader("Minhas Vagas e Candidatos")
    vagas = supabase.table("vagas").select("*").eq("empresa_id", user["id"]).execute().data

    if not vagas:
        st.info("Você ainda não criou nenhuma vaga.")
        return

    for vaga in vagas:
        st.markdown("---")
        st.markdown(f"### 📌 {vaga['titulo']}")
        st.markdown(f"{vaga.get('descricao', 'Sem descrição.')}")
        st.markdown(f"**Criada em:** `{vaga.get('criada_em', '')}`")
        st.markdown(f"**Quantidade de Vagas:** `{vaga.get('quantidade', 1)}`")

        # Botão para cancelar a vaga
        if st.button("❌ Cancelar esta vaga", key=f"cancelar_{vaga['id']}"):
            try:
                supabase.table("vagas").delete().eq("id", vaga["id"]).execute()
                st.success("Vaga cancelada com sucesso.")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao cancelar a vaga: {e}")
            continue

        # Candidatos vinculados à vaga
        log = supabase.table("log_vinculos_estudantes_vagas") \
            .select("*") \
            .eq("vaga_id", vaga["id"]).execute().data

        if not log:
            st.info("Nenhum estudante vinculado a esta vaga ainda.")
            continue

        st.markdown("#### 🎓 Candidatos:")

        for entrada in log:
            estudante_id = entrada["estudante_id"]
            estudante_info = supabase.table("estudantes") \
                .select("nome, email") \
                .eq("id", estudante_id).execute().data

            if not estudante_info:
                continue

            estudante = estudante_info[0]
            nome = estudante["nome"]
            email = estudante["email"]
            status = entrada["status"]
            prazo_str = entrada.get("prazo_resposta")

            prazo = datetime.fromisoformat(prazo_str.replace("Z", "+00:00")) if prazo_str else None

            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(f"**👤 {nome}** ({email})")
                st.markdown(f"📌 Status: `{status}`")
                if prazo:
                    st.markdown(f"📅 Prazo: `{prazo.strftime('%d/%m/%Y %H:%M UTC')}`")

            with col2:
                if status == "notificado":
                    if st.button(f"✅ Contratar {nome}", key=f"contratar_{entrada['id']}"):
                        try:
                            supabase.table("log_vinculos_estudantes_vagas") \
                                .update({"status": "contratado"}) \
                                .eq("id", entrada["id"]).execute()
                    
                            # Conta quantos já foram contratados para essa vaga
                            contratados_res = supabase.table("log_vinculos_estudantes_vagas") \
                                .select("id") \
                                .eq("vaga_id", vaga['id']) \
                                .eq("status", "contratado").execute()
                    
                            total_contratados = len(contratados_res.data or [])
                    
                            if total_contratados < vaga['quantidade']:
                                from controller.vagas_controller import chamar_proximos_estudantes_disponiveisv3
                                chamar_proximos_estudantes_disponiveisv3(supabase, vaga['id'], 1)                            
                            
                            #from controller.vagas_controller import chamar_proximos_estudantes_disponiveisv3
                            #chamar_proximos_estudantes_disponiveisv3(supabase, vaga['id'],1)
                            
                            from controller.email_controller import enviar_email
                            assunto = "Parabéns! Você foi contratado"
                            corpo = f"""
Olá {nome},

Temos o prazer de informar que você foi contratado para a vaga '{vaga['titulo']}'.

Parabéns e sucesso na sua nova etapa!

Atenciosamente,
Sistema de Estágios
"""
                            try:
                                enviar_email(email, assunto, corpo)
                                st.info("Email de contratação enviado.")
                            except Exception as email_err:
                                st.warning(f"⚠️ Email não foi enviado: {email_err}")

                            st.success(f"{nome} foi marcado como contratado.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao contratar: {e}")

                    with st.expander(f"📩 Recusar {nome} com justificativa", expanded=False):
                        justificativa = st.text_area(
                            f"Justificativa para recusar {nome}",
                            key=f"just_{entrada['id']}"
                        )
                        if st.button(f"Recusar {nome}", key=f"recusar_{entrada['id']}"):
                            if justificativa.strip() == "":
                                st.warning("Escreva uma justificativa antes de recusar.")
                            else:
                                try:
                                    # Atualiza status para recusado
                                    supabase.table("log_vinculos_estudantes_vagas") \
                                        .update({"status": "recusado"}) \
                                        .eq("id", entrada["id"]) \
                                        .execute()

                                    st.success(f"{nome} foi recusado com justificativa.")

                                    # Atualiza a lista chamando próximos estudantes antes de enviar o email
                                    from controller.vagas_controller import chamar_proximos_estudantes_disponiveisv3
                                    chamar_proximos_estudantes_disponiveisv3(supabase, vaga['id'],1)

                                    #enviados = 0
                                    #for estudante_id, media in estudantes_ordenados:
                                    #    supabase.table("log_vinculos_estudantes_vagas").insert({
                                    #        "estudante_id": estudante_id,
                                    #        "vaga_id": vaga['id'],
                                    #        "status": "notificado",
                                    #        "prazo_resposta": prazo.isoformat()
                                    #    }).execute()

                                    
                                    # Tenta enviar email informando a recusa
                                    try:
                                        from controller.email_controller import enviar_email

                                        assunto = "Atualização sobre sua candidatura"
                                        corpo = f"""
Olá {nome},

Agradecemos seu interesse na vaga '{vaga['titulo']}'.

Infelizmente, você não foi selecionado para avançar neste processo seletivo.

Motivo da recusa informado pela empresa:
"{justificativa}"

Desejamos sucesso em suas próximas candidaturas.

Atenciosamente,  
Sistema de Estágios
"""

                                        enviar_email(email, assunto, corpo)
                                        st.info("Email de recusa enviado.")
                                    except Exception as email_err:
                                        st.warning(f"⚠️ Email não foi enviado: {email_err}")

                                    # Atualiza a página para refletir as mudanças
                                    st.rerun()

                                except Exception as e:
                                    st.error(f"Erro ao recusar estudante: {e}")
