# controller/vagas_controller.py

def selecionar_estudantes_para_vaga(supabase, vaga_id, quantidade):
    # Buscar info da vaga (curso e disciplinas)
    vaga_res = supabase.table("vagas").select("curso_id").eq("id", vaga_id).execute()
    if not vaga_res.data:
        return []

    curso_id = vaga_res.data[0]["curso_id"]

    disciplinas_res = supabase.table("vagas_disciplinas").select("disciplina_id").eq("vaga_id", vaga_id).execute()
    disciplinas_ids = [d["disciplina_id"] for d in disciplinas_res.data]

    if not disciplinas_ids:
        return []

    # Buscar estudantes ativos do curso
    estudantes_res = supabase.table("estudantes").select("id").eq("curso_id", curso_id).eq("ativo", True).execute()
    estudantes_ids = [e["id"] for e in estudantes_res.data]

    if not estudantes_ids:
        return []

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

    # Ordenar pelo rendimento decrescente
    estudantes_medias.sort(key=lambda x: x[1], reverse=True)

    # Retornar apenas a quantidade solicitada
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

        # Evita duplicidade
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


