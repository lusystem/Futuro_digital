from tests.test_aluno import criar_aluno_base

def criar_escola_base(client, auth_headers):
    response = client.post("/escolas/criar", data = {
        "nome": "Escola Base", 
        "endereco": "Rua Base, 123",
        "tipo": "Publica",
        "quantidade_turmas": 5,
        "vagas": 200,
        "capacidade_alunos": 500
    }, headers=auth_headers)
    return response.get_json()["id_escola"]

def test_criar_turma(client, auth_headers):
    id_escola = criar_escola_base(client, auth_headers)
    response = client.post("/turmas/criar", data = {
        "nome": "Turma A",
        "serie": "1º Ano",
        "capacidade_maxima": 30,
        "id_escola": id_escola
    }, headers=auth_headers)
    assert response.status_code == 201

    data = response.get_json()
    assert "id_turma" in data
    assert data["nome"] == "Turma A"
    assert data["serie"] == "1º Ano"
    assert data["capacidade_maxima"] == 30
    assert data["id_escola"] == id_escola

def test_ver_turma(client, auth_headers):
    id_escola = criar_escola_base(client, auth_headers)

    criar = client.post("/turmas/criar", data = {
        "nome": "Turma B",
        "serie": "2º Ano",
        "capacidade_maxima": 25,
        "id_escola": id_escola
    }, headers=auth_headers)
    id_turma = criar.get_json()["id_turma"]

    response = client.get(f"/turmas/ver/{id_turma}", headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["id_turma"] == id_turma
    assert data["nome"] == "Turma B"
    assert data["serie"] == "2º Ano"

def test_atualizar_turma(client, auth_headers):
    id_escola = criar_escola_base(client, auth_headers)
    criar = client.post("/turmas/criar", data = {
        "nome": "Turma C",
        "serie": "3º Ano",
        "capacidade_maxima": 20,
        "id_escola": id_escola
    }, headers=auth_headers)
    id_turma = criar.get_json()["id_turma"]
    response = client.put(f"/turmas/atualizar/{id_turma}", data = {
        "nome": "Turma C Atualizada",
        "serie": "4º Ano",
        "capacidade_maxima": 35,
        "id_escola": id_escola
    }, headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert data["nome"] == "Turma C Atualizada"
    assert data["serie"] == "4º Ano"
    assert data["capacidade_maxima"] == 35

def test_deletar_turma(client, auth_headers):
    id_escola = criar_escola_base(client, auth_headers)
    criar = client.post("/turmas/criar", data = {
        "nome": "Turma D",
        "serie": "5º Ano",
        "capacidade_maxima": 40,
        "id_escola": id_escola
    }, headers=auth_headers)
    id_turma = criar.get_json()["id_turma"]

    response = client.delete(f"/turmas/deletar/{id_turma}", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json()["mensagem"] == "Turma deletada com sucesso"

    verificar = client.get(f"/turmas/ver/{id_turma}", headers=auth_headers)
    assert verificar.status_code == 404

def test_listar_turmas(client, auth_headers):
    id_escola = criar_escola_base(client, auth_headers)
    client.post("/turmas/criar", data = {
        "nome": "Turma E",
        "serie": "6º Ano",
        "capacidade_maxima": 28,
        "id_escola": id_escola
    }, headers=auth_headers)
    response = client.get("/turmas/listar", headers=auth_headers)
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_turma_lotada(client, auth_headers):
    id_escola = criar_escola_base(client, auth_headers)
    criar = client.post("/turmas/criar", data = {
        "nome": "Turma Pequena",
        "serie": "1º Ano",
        "capacidade_maxima": 1,
        "id_escola": id_escola
    }, headers=auth_headers)
    id_turma = criar.get_json()["id_turma"]
    
    client.post("/alunos/criar", data = {
        "nome": "Aluno 1",
        "idade": "15",
        "id_turma": str(id_turma)
    }, headers=auth_headers)
    response = client.post("/alunos/criar", data = {
        "nome": "Aluno 2",
        "idade": "16",
        "id_turma": str(id_turma)
    }, headers=auth_headers)
    assert response.status_code == 400
    assert "Turma lotada" in response.get_json()["erro"]

def test_libera_vaga_ao_deletar(client, auth_headers):
    id_turma = criar_aluno_base(client, auth_headers)
    aluno = client.post("/alunos/criar", data = {
        "nome": "Aluno Teste",
        "idade": "15",
        "id_turma": str(id_turma)
    }, headers=auth_headers).get_json()
    client.delete(f"/alunos/deletar/{aluno['id_aluno']}", headers=auth_headers)

    response = client.post("/alunos/criar", data = {
        "nome": "Novo Aluno",
        "idade": "16",
        "id_turma": str(id_turma)
    }, headers=auth_headers)
    assert response.status_code == 201

def test_vagas_turma(client, auth_headers):
    id_turma = criar_aluno_base(client, auth_headers)

    response = client.get(f"/turmas/vagas_restantes/{id_turma}", headers=auth_headers)
    data = response.get_json()

    assert response.status_code == 200
    assert "vagas_restantes" in data