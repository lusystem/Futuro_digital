def criar_escola_base(client):
    response = client.post("/escolas", data={
        "nome": "Escola Base",
        "endereco": "Rua Base, 123",
        "tipo": "Publica",
        "quantidade_turmas": 5,
        "vagas": 200,
        "capacidade_alunos": 500
    })
    return response.get_json()["id_escola"]

def test_criar_turma(client):
    id_escola = criar_escola_base(client)
    response = client.post("/turma/criar", data={
        "nome": "Turma A",
        "serie": "1º Ano",
        "capacidade_maxima": 30,
        "id_escola": id_escola
    })
    assert response.status_code == 201

    data = response.get_json()
    assert "id_turma" in data
    assert data["nome"] == "Turma A"
    assert data["serie"] == "1º Ano"
    assert data["capacidade_maxima"] == 30
    assert data["id_escola"] == id_escola

def test_ver_turma(client):
    id_escola = criar_escola_base(client)

    criar = client.post("/turma/criar", data={
        "nome": "Turma B",
        "serie": "2º Ano",
        "capacidade_maxima": 25,
        "id_escola": id_escola
    })
    id_turma = criar.get_json()["id_turma"]

    response = client.get(f"/turma/ver_uma/{id_turma}")
    assert response.status_code == 200

    data = response.get_json()
    assert data["id_turma"] == id_turma
    assert data["nome"] == "Turma B"
    assert data["serie"] == "2º Ano"

def test_atualizar_turma(client):
    id_escola = criar_escola_base(client)
    criar = client.post("/turma/criar", data={
        "nome": "Turma C",
        "serie": "3º Ano",
        "capacidade_maxima": 20,
        "id_escola": id_escola
    })
    id_turma = criar.get_json()["id_turma"]
    response = client.put(f"/turma/atualizar/{id_turma}", data={
        "nome": "Turma C Atualizada",
        "serie": "4º Ano",
        "capacidade_maxima": 35,
        "id_escola": id_escola
    })
    assert response.status_code == 200

    data = response.get_json()
    assert data["nome"] == "Turma C Atualizada"
    assert data["serie"] == "4º Ano"
    assert data["capacidade_maxima"] == 35

def test_deletar_turma(client):
    id_escola = criar_escola_base(client)
    criar = client.post("/turma/criar", data={
        "nome": "Turma D",
        "serie": "5º Ano",
        "capacidade_maxima": 40,
        "id_escola": id_escola
    })
    id_turma = criar.get_json()["id_turma"]

    response = client.delete(f"/turma/deletar/{id_turma}")
    assert response.status_code == 200
    assert response.get_json()["mensagem"] == "Turma deletada com sucesso"

    verificar = client.get(f"/turma/ver_uma/{id_turma}")
    assert verificar.status_code == 404

def test_listar_turmas(client):
    id_escola = criar_escola_base(client)
    client.post("/turma/criar", data={
        "nome": "Turma E",
        "serie": "6º Ano",
        "capacidade_maxima": 28,
        "id_escola": id_escola
    })
    response = client.get("/turma/ver")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1