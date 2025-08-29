import os
from mailersend import MailerSendClient, EmailBuilder
from mailersend.exceptions import MailerSendError
from datetime import datetime

# Pega as variáveis do ambiente
API_KEY = os.getenv("MAILERSEND_API_KEY")
FROM_EMAIL = os.getenv("MAILERSEND_FROM_EMAIL")
FROM_NAME = os.getenv("MAILERSEND_FROM_NAME")

client = MailerSend(api_key=API_KEY)

def enviar_email(destinatario, assunto, corpo):
    message = Message(
        from_email={"email": FROM_EMAIL, "name": FROM_NAME},
        to=[{"email": destinatario}],
        subject=assunto,
        text=corpo,
    )
    response = client.send(message)
    return response

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

    try:
        enviar_email(email_estudante, assunto, corpo)
        return True, None
    except Exception as e:
        return False, str(e)
