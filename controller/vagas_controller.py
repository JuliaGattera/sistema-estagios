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

