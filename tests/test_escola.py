def test_criar_escola(client, auth_headers):
    response = client.post("/escolas/criar", data={
        "nome": "Escola Central",
        "endereco": "Rua Principal, 100",
        "tipo": "Publica",
        "quantidade_turmas": 10,
        "vagas": 200,
        "capacidade_alunos": 500
    }, headers=auth_headers)
    assert response.status_code == 201

    data = response.get_json()
    assert "id_escola" in data
    assert data["nome"] == "Escola Central"
    assert data["endereco"] == "Rua Principal, 100"
    assert data["tipo"] == "Publica"
    assert data["quantidade_turmas"] == 10
    assert data["vagas"] == 200
    assert data["capacidade_alunos"] == 500

def test_ver_escola(client, auth_headers):
    criar_response = client.post("/escolas/criar", data={
        "nome": "Escola Teste",
        "endereco": "Rua Teste, 123",
        "tipo": "Privada",
        "quantidade_turmas": 5,
        "vagas": 100,
        "capacidade_alunos": 300
    }, headers=auth_headers)
    escola_id = criar_response.get_json()["id_escola"]

    ver_response = client.get(f"/escolas/ver/{escola_id}", headers=auth_headers)
    assert ver_response.status_code == 200

    data = ver_response.get_json()
    assert data["id_escola"] == escola_id
    assert data["nome"] == "Escola Teste"
    assert data["endereco"] == "Rua Teste, 123"
    assert data["tipo"] == "Privada"
    assert data["quantidade_turmas"] == 5
    assert data["vagas"] == 100
    assert data["capacidade_alunos"] == 300

def test_atualizar_escola(client, auth_headers):
    criar_response = client.post("/escolas/criar", data={
        "nome": "Escola Atualizada",
        "endereco": "Rua Atualizada, 789",
        "tipo": "Publica",
        "quantidade_turmas": 12,
        "vagas": 250,
        "capacidade_alunos": 600
    }, headers=auth_headers)
    escola_id = criar_response.get_json()["id_escola"]

    atualizar_response = client.put(f"/escolas/atualizar/{escola_id}", data={
        "nome": "Escola Atualizada Nova",
        "endereco": "Rua Atualizada Nova, 789",
        "tipo": "Privada",
        "quantidade_turmas": 15,
        "vagas": 300,
        "capacidade_alunos": 700
    }, headers=auth_headers)
    assert atualizar_response.status_code == 200

    data = atualizar_response.get_json()
    assert data["id_escola"] == escola_id
    assert data["nome"] == "Escola Atualizada Nova"
    assert data["endereco"] == "Rua Atualizada Nova, 789"
    assert data["tipo"] == "Privada"
    assert data["quantidade_turmas"] == 15
    assert data["vagas"] == 300
    assert data["capacidade_alunos"] == 700

    ver_response = client.get(f"/escolas/ver/{escola_id}", headers=auth_headers)
    assert ver_response.status_code == 200
    
    ver_data = ver_response.get_json()
    assert ver_data["nome"] == "Escola Atualizada Nova"
    assert ver_data["tipo"] == "Privada"

def test_deletar_escola(client, auth_headers):
    criar_response = client.post("/escolas/criar", data={
        "nome": "Escola a Deletar",
        "endereco": "Rua Deletar, 456",
        "tipo": "Publica",
        "quantidade_turmas": 8,
        "vagas": 150,
        "capacidade_alunos": 400
    }, headers=auth_headers)
    escola_id = criar_response.get_json()["id_escola"]

    deletar_response = client.delete(f"/escolas/deletar/{escola_id}", headers=auth_headers)
    assert deletar_response.status_code == 200

    data = deletar_response.get_json()
    assert data["mensagem"] == "Escola deletada com sucesso."

    ver_response = client.get(f"/escolas/ver/{escola_id}", headers=auth_headers)
    assert ver_response.status_code == 404
    assert ver_response.get_json()["erro"] == "Escola não encontrada."

def test_listar_escolas(client, auth_headers):
    client.post("/escolas/criar", data={
        "nome": "Escola A",
        "endereco": "Rua A",
        "tipo": "Publica",
        "quantidade_turmas": 5,
        "vagas": 100,
        "capacidade_alunos": 300
    }, headers=auth_headers)
    response = client.get("/escolas/listar", headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1