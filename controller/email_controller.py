from datetime import datetime
from mailersend import emails
import streamlit as st

def enviar_email(destinatario, assunto, corpo):
    mailer = emails.NewEmail()
    
    mailer.set_api_key(st.secrets["mailersend"]["api_token"])

    mailer.set_from({
        "email": st.secrets["mailersend"]["sender_email"],
        "name": st.secrets["mailersend"]["sender_name"]
    })

    mailer.set_to([{
        "email": destinatario
    }])

    mailer.set_subject(assunto)
    mailer.set_text_content(corpo)

    try:
        mailer.send()
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        raise

def notificar_estudante_por_email(supabase, estudante_id, vaga_info, empresa_info, prazo_resposta):
    # Buscar dados do estudante
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

    # Enviar o email
    try:
        enviar_email(email_estudante, assunto, corpo)
        return True, None
    except Exception as e:
        return False, str(e)
