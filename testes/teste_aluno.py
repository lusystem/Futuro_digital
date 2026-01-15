def criar_aluno_base(client):
    response = client.post("/escolas", data={
        "nome": "Escola Base",
        "endereco": "Rua Principal, 123",
        "tipo": "Publica",
        "quantidade_turmas": "5",
        "vagas": "200",
        "capacidade_alunos": "500"
    })
    id_escola = response.get_json()["id_escola"]
    response = client.post("/turma/criar", data={
        "nome": "Turma Base",
        "serie": "1º Ano",
        "capacidade_maxima": "30",
        "id_escola": str(id_escola)
    })
    id_turma = response.get_json()["id_turma"]
    response = client.post("/aluno/criar", data={
        "nome": "Aluno Base",
        "idade": "15",
        "id_turma": str(id_turma)
    })
    return id_turma

def test_criar_aluno(client):
    id_turma = criar_aluno_base(client)
    response = client.post("/aluno/criar", data={
        "nome": "João Silva",
        "idade": "16",
        "id_turma": str(id_turma)
    })
    assert response.status_code == 201

    data = response.get_json()
    assert "id_aluno" in data
    assert data["nome"] == "João Silva"
    assert data["idade"] == 16
    assert data["id_turma"] == id_turma

def test_atualizar_aluno(client):
    id_turma = criar_aluno_base(client)
    criar = client.post("/aluno/criar", data={
        "nome": "Pedro Santos",
        "idade": "17",
        "id_turma": str(id_turma)
    })
    id_aluno = criar.get_json()["id_aluno"]
    response = client.put(f"/aluno/atualizar/{id_aluno}", data={
        "nome": "Pedro Santos Atualizado",
        "idade": "18",
        "id_turma": str(id_turma)
    })
    assert response.status_code == 200

    data = response.get_json()
    assert data["id_aluno"] == id_aluno
    assert data["nome"] == "Pedro Santos Atualizado"
    assert data["idade"] == 18

def test_ver_aluno(client):
    id_turma = criar_aluno_base(client)

    criar = client.post("/aluno/criar", data={
        "nome": "Maria Oliveira",
        "idade": "14",
        "id_turma": str(id_turma)
    })
    id_aluno = criar.get_json()["id_aluno"]

    response = client.get(f"/aluno/ver_uma/{id_aluno}")
    assert response.status_code == 200

    data = response.get_json()
    assert data["id_aluno"] == id_aluno
    assert data["nome"] == "Maria Oliveira"
    assert data["idade"] == 14

def test_deletar_aluno(client):
    id_turma = criar_aluno_base(client)
    criar = client.post("/aluno/criar", data={
        "nome": "Lucas Pereira",
        "idade": "15",
        "id_turma": str(id_turma)
    })
    id_aluno = criar.get_json()["id_aluno"]
    response = client.delete(f"/aluno/deletar/{id_aluno}")
    assert response.status_code == 200
    assert response.get_json()["mensagem"] == "Aluno deletado com sucesso"

    verificar = client.get(f"/aluno/ver_uma/{id_aluno}")
    assert verificar.status_code == 404

def test_listar_alunos(client):
    id_turma = criar_aluno_base(client)
    client.post("/aluno/criar", data={
        "nome": "Ana Costa",
        "idade": "13",
        "id_turma": str(id_turma)
    })
    client.post("/aluno/criar", data={
        "nome": "Bruno Lima",
        "idade": "14",
        "id_turma": str(id_turma)
    })

    response = client.get("/aluno/ver")
    assert response.status_code == 200

    data = response.get_json()
    assert len(data) >= 2 