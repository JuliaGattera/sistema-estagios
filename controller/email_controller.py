from datetime import datetime
import streamlit as st
from mailersend import MailerSendClient, EmailBuilder
from mailersend.exceptions import MailerSendError

def enviar_email(destinatario, assunto, corpo):
    # Inicializa o cliente com API key do secrets
    ms = MailerSendClient(api_key=st.secrets["mailersend"]["api_key"])
    
    # Constrói o e-mail
    email = (EmailBuilder()
             .from_email(
                 st.secrets["mailersend"]["from_email"],
                 st.secrets["mailersend"]["from_name"]
             )
             .to_many([{"email": destinatario}])
             .subject(assunto)
             .text(corpo)
             .build())
    try:
        # Envia o e-mail
        ms.emails.send(email)
        return True, None
    except MailerSendError as e:
        # Captura erros específicos da API
        st.error(f"MailerSend API Error: {e}")
        return False, str(e)
    except Exception as e:
        st.error(f"Erro inesperado ao enviar e-mail: {e}")
        return False, str(e)

def notificar_estudante_por_email(supabase, estudante_id, vaga_info, empresa_info, prazo_resposta):
    estudante_res = supabase.table("estudantes").select("email, nome").eq("id", estudante_id).execute()
    if not estudante_res.data:
        return False, "Estudante não encontrado."

    estudante = estudante_res.data[0]
    email_estudante = estudante["email"]
    nome_estudante = estudante["nome"]

    assunto = "Você foi selecionado para uma vaga de estágio"
    corpo = f"""
Olá {nome_estudante},

Você foi selecionado para participar do processo seletivo da vaga '{vaga_info['titulo']}' na empresa {empresa_info['nome']}.

Detalhes da vaga:
Título: {vaga_info['titulo']}
Descrição: {vaga_info.get('descricao', 'Sem descrição disponível')}
Contato da empresa: {empresa_info.get('email', 'Não informado')}

Prazo para resposta: {prazo_resposta.strftime('%d/%m/%Y %H:%M UTC')}

Acesse o sistema para aceitar ou recusar a vaga.

Boa sorte!

Atenciosamente,
Equipe de Estágios
"""

    return enviar_email(email_estudante, assunto, corpo)
