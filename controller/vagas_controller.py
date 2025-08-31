# controller/vagas_controller.py
from datetime import datetime, timezone, timedelta

def selecionar_estudantes_para_vaga(supabase, vaga_id, quantidade):
    # Buscar info da vaga (curso e disciplinas)
    vaga_res = supabase.table("vagas").select("curso_id").eq("id", vaga_id).execute()
    if not vaga_res.data:
        return []

    curso_id = vaga_res.data[0]["curso_id"]

    # Buscar disciplinas associadas à vaga
    disciplinas_res = supabase.table("vagas_disciplinas").select("disciplina_id").eq("vaga_id", vaga_id).execute()
    disciplinas_ids = [d["disciplina_id"] for d in disciplinas_res.data]

    if not disciplinas_ids:
        return []

    # Buscar estudantes ativos do curso
    estudantes_res = supabase.table("estudantes").select("id").eq("curso_id", curso_id).eq("ativo", True).execute()
    estudantes_ids = [e["id"] for e in estudantes_res.data]

    if not estudantes_ids:
        return []

    # Buscar candidatos que já foram chamados ou contratados (evitar duplicidade)
    log_res = supabase.table("log_vinculos_estudantes_vagas")\
        .select("estudante_id", "status")\
        .eq("vaga_id", vaga_id)\
        .in_("status", ["notificado", "contratado"]).execute()

    ja_chamados_ids = {r["estudante_id"] for r in log_res.data}

    # Filtra os estudantes que ainda não foram chamados
    estudantes_ids = [e for e in estudantes_ids if e not in ja_chamados_ids]

    estudantes_medias = []

    for estudante_id in estudantes_ids:
        # Buscar notas do estudante nas disciplinas exigidas
        notas_res = supabase.table("notas_estudantes")\
            .select("nota")\
            .eq("estudante_id", estudante_id)\
            .in_("disciplina_id", disciplinas_ids)\
            .execute()

        notas = [n["nota"] for n in notas_res.data if n["nota"] is not None]

        if notas:
            media = sum(notas) / len(notas)
            estudantes_medias.append((estudante_id, media))

    # Ordenar os estudantes pelo desempenho
    estudantes_medias.sort(key=lambda x: x[1], reverse=True)

    # Retornar a quantidade solicitada de estudantes
    return estudantes_medias[:quantidade]


def vagas_disponiveis_para_estudante(supabase, user_id: str, nota_minima=7.0):
    estudante_res = supabase.table("estudantes").select("id, curso_id").eq("user_id", user_id).execute()
    if not estudante_res.data:
        return []

    estudante = estudante_res.data[0]
    estudante_id = estudante["id"]
    curso_id = estudante["curso_id"]

    vagas_res = supabase.table("vagas").select("id, titulo, descricao").eq("curso_id", curso_id).execute()
    vagas = vagas_res.data
    vagas_filtradas = []

    for vaga in vagas:
        vaga_id = vaga["id"]
        vagas_disciplinas_res = supabase.table("vagas_disciplinas").select("disciplina_id").eq("vaga_id", vaga_id).execute()
        disciplinas_ids = [d["disciplina_id"] for d in vagas_disciplinas_res.data]

        notas_res = supabase.table("notas_estudantes").select("disciplina_id, nota").eq("estudante_id", estudante_id).in_("disciplina_id", disciplinas_ids).execute()
        notas = notas_res.data
        notas_dict = {n["disciplina_id"]: n["nota"] for n in notas}
        atende = all(notas_dict.get(did, 0) >= nota_minima for did in disciplinas_ids)

        if atende:
            vagas_filtradas.append(vaga)

    return vagas_filtradas

from datetime import datetime, timedelta
from controller.email_controller import notificar_estudante_por_email

def chamar_proximos_estudantes_disponiveis(supabase, vaga_id):
    # Buscar vaga
    vaga_res = supabase.table("vagas").select("*").eq("id", vaga_id).execute()
    if not vaga_res.data:
        return

    vaga = vaga_res.data[0]
    quantidade_maxima = vaga.get("quantidade", 1) * 2

    # Ver quantos estudantes já foram notificados ou contratados
    log_res = supabase.table("log_vinculos_estudantes_vagas") \
        .select("id, estudante_id, status") \
        .eq("vaga_id", vaga_id).execute()

    log_data = log_res.data or []
    ja_chamados_ids = {r["estudante_id"] for r in log_data if r["status"] in ["notificado", "contratado"]}

    if len(ja_chamados_ids) >= quantidade_maxima:
        return  # já atingiu o limite

    faltam_chamar = quantidade_maxima - len(ja_chamados_ids)

    # Selecionar candidatos elegíveis
    candidatos = selecionar_estudantes_para_vaga(supabase, vaga_id, quantidade=faltam_chamar)
    candidatos_a_chamar = [(eid, media) for (eid, media) in candidatos if eid not in ja_chamados_ids]
    print(f"[DEBUG] Candidatos elegíveis encontrados para chamar: {len(candidatos_a_chamar)}")
    
    for estudante_id, _ in candidatos_a_chamar:
        prazo_resposta = datetime.now(tz=timezone.utc) + timedelta(days=2)

        # Evita duplicidade: inserir novo vínculo
        try:
            supabase.table("log_vinculos_estudantes_vagas").insert({
                "vaga_id": vaga_id,
                "estudante_id": estudante_id,
                "status": "notificado",
                "prazo_resposta": prazo_resposta.isoformat()
            }).execute()
        except Exception as insert_err:
            continue  # já foi chamado anteriormente, provavelmente por chave única

        # Buscar info da empresa
        empresa_res = supabase.table("empresas").select("*").eq("id", vaga["empresa_id"]).execute()
        empresa = empresa_res.data[0] if empresa_res.data else {}

        # Enviar e-mail
        notificar_estudante_por_email(supabase, estudante_id, vaga, empresa, prazo_resposta)

def chamar_proximos_estudantes_disponiveisv2(supabase, vaga_id, quantidade):
    # Buscar info da vaga (curso e disciplinas)
    vaga_res = supabase.table("vagas").select("curso_id").eq("id", vaga_id).execute()
    if not vaga_res.data:
        return []

    curso_id = vaga_res.data[0]["curso_id"]

    # Buscar disciplinas associadas à vaga
    disciplinas_res = supabase.table("vagas_disciplinas").select("disciplina_id").eq("vaga_id", vaga_id).execute()
    disciplinas_ids = [d["disciplina_id"] for d in disciplinas_res.data]

    if not disciplinas_ids:
        return []

    # Buscar estudantes ativos do curso
    estudantes_res = supabase.table("estudantes").select("id").eq("curso_id", curso_id).eq("ativo", True).execute()
    estudantes_ids = [e["id"] for e in estudantes_res.data]

    if not estudantes_ids:
        return []

    # Buscar candidatos que já foram chamados ou contratados (evitar duplicidade)
    log_res = supabase.table("log_vinculos_estudantes_vagas")\
        .select("estudante_id", "status")\
        .eq("vaga_id", vaga_id)\
        .in_("status", ["notificado", "contratado", "recusado", "desistente"]).execute()

    ja_chamados_ids = {r["estudante_id"] for r in (log_res.data or [])}

    # Filtra os estudantes que ainda não foram chamados
    estudantes_ids = [e for e in estudantes_ids if e not in ja_chamados_ids]

    estudantes_medias = []

    for estudante_id in estudantes_ids:
        # Buscar notas do estudante nas disciplinas exigidas
        notas_res = supabase.table("notas_estudantes")\
            .select("nota")\
            .eq("estudante_id", estudante_id)\
            .in_("disciplina_id", disciplinas_ids)\
            .execute()

        notas = [n["nota"] for n in notas_res.data if n["nota"] is not None]

        if notas:
            media = sum(notas) / len(notas)
            estudantes_medias.append((estudante_id, media))

    # Ordenar os estudantes pelo desempenho
    estudantes_medias.sort(key=lambda x: x[1], reverse=True)

    # Retornar a quantidade solicitada de estudantes
    return estudantes_medias[:quantidade]

from datetime import datetime, timezone, timedelta

def chamar_proximos_estudantes_disponiveisv3(supabase, vaga_id, quantidade):
    # Buscar info da vaga (curso e disciplinas)
    vaga_res = supabase.table("vagas").select("curso_id").eq("id", vaga_id).execute()
    if not vaga_res.data:
        return []

    curso_id = vaga_res.data[0]["curso_id"]

    # Buscar disciplinas associadas à vaga
    disciplinas_res = supabase.table("vagas_disciplinas").select("disciplina_id").eq("vaga_id", vaga_id).execute()
    disciplinas_ids = [d["disciplina_id"] for d in disciplinas_res.data]

    if not disciplinas_ids:
        return []

    # Buscar estudantes ativos do curso
    estudantes_res = supabase.table("estudantes").select("id").eq("curso_id", curso_id).eq("ativo", True).execute()
    estudantes_ids = [e["id"] for e in estudantes_res.data]

    if not estudantes_ids:
        return []

    # Buscar candidatos que já foram chamados ou contratados ou recusados
    log_res = supabase.table("log_vinculos_estudantes_vagas") \
        .select("estudante_id", "status") \
        .eq("vaga_id", vaga_id) \
        .in_("status", ["notificado", "contratado", "recusado"]).execute()

    ja_chamados_ids = {r["estudante_id"] for r in (log_res.data or [])}

    # Filtra os estudantes que ainda não foram chamados
    estudantes_ids = [e for e in estudantes_ids if e not in ja_chamados_ids]

    estudantes_medias = []

    for estudante_id in estudantes_ids:
        notas_res = supabase.table("notas_estudantes") \
            .select("nota") \
            .eq("estudante_id", estudante_id) \
            .in_("disciplina_id", disciplinas_ids) \
            .execute()

        notas = [n["nota"] for n in notas_res.data if n["nota"] is not None]

        if notas:
            media = sum(notas) / len(notas)
            estudantes_medias.append((estudante_id, media))

    # Ordenar estudantes por nota
    estudantes_medias.sort(key=lambda x: x[1], reverse=True)

    # Seleciona os N estudantes
    selecionados = estudantes_medias[:quantidade]

    # Inserir no banco com status "notificado" e prazo em 2 dias
    prazo = datetime.now(timezone.utc) + timedelta(days=2)

    for estudante_id, media in selecionados:
        supabase.table("log_vinculos_estudantes_vagas").insert({
            "estudante_id": estudante_id,
            "vaga_id": vaga_id,
            "status": "notificado",
            "prazo_resposta": prazo.isoformat()
        }).execute()

    #return selecionados  # opcional, caso precise retornar

def encerrar_vaga_automaticamente(supabase, vaga_id, vaga_titulo):
    # Exclui a vaga (ou marque como encerrada, se preferir)
    supabase.table("vagas").delete().eq("id", vaga_id).execute()

    # Busca estudantes notificados que ainda não foram contratados ou recusados
    log = supabase.table("log_vinculos_estudantes_vagas") \
        .select("id, estudante_id") \
        .eq("vaga_id", vaga_id) \
        .eq("status", "notificado") \
        .execute().data

    for entrada in log:
        estudante_id = entrada["estudante_id"]

        estudante_info = supabase.table("estudantes") \
            .select("email, nome") \
            .eq("id", estudante_id).execute().data

        if not estudante_info:
            continue

        estudante = estudante_info[0]
        email = estudante["email"]
        nome = estudante["nome"]

        # Atualiza status como recusado
        supabase.table("log_vinculos_estudantes_vagas") \
            .update({"status": "recusado"}) \
            .eq("id", entrada["id"]).execute()

        # Envia e-mail informando o encerramento da vaga
        from controller.email_controller import enviar_email
        assunto = "Vaga encerrada"
        corpo = f"""
Olá {nome},

A vaga '{vaga_titulo}' foi encerrada, pois todas as posições foram preenchidas.

Agradecemos seu interesse e desejamos sucesso nas suas futuras candidaturas!

Atenciosamente,  
Sistema de Estágios
"""
        try:
            enviar_email(email, assunto, corpo)
        except Exception as e:
            print(f"Erro ao enviar e-mail para {email}: {e}")



