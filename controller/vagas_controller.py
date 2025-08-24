# controller/vagas_controller.py
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

