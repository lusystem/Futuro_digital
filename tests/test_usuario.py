from control import seguranca

def criar_escola(client):
    response = client.post("/escolas/", data = {
        "nome": "Escola Teste",
        "endereco": "Rua Teste",
        "tipo": "Publica",
        "quantidade_turmas": 10,
        "vagas": 100,
        "capacidade_alunos": 30
    })
    assert response.status_code == 201
    return response.get_json()["id_escola"]

def criar_usuario_base(client):
    id_escola = criar_escola(client)
    response = client.post("/cadastro/", data = {
        "nome_usuario": "Usuário Teste",
        "email": "teste@email.com",
        "senha": "123456",
        "cargo": "admin",
        "id_escola": id_escola
    })
    assert response.status_code == 201
    return response.get_json()

def test_cadastro_usuario(client):
    id_escola = criar_escola(client)
    response = client.post("/cadastro/", data = {
        "nome_usuario": "João",
        "email": "joao@email.com",
        "senha": "123456",
        "cargo": "admin",
        "id_escola": id_escola 
    })
    assert response.status_code == 201

    data = response.get_json()
    assert "id_usuario" in data
    assert data["email"] == "joao@email.com"

def test_login_usuario(client):
    criar_usuario_base(client)
    response = client.post("/login/", data = {
        "email": "teste@email.com",
        "senha": "123456"
    })
    assert response.status_code == 200
    
    data = response.get_json()
    assert "id_usuario" in data
    assert data["email"] == "teste@email.com"

def test_login_usuario_invalido(client):
    response = client.post("/login/", data = {
        "email": "",
        "senha": 'senhaa'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "erro" in data

def test_login_usuario_inexistente(client):
    response = client.post("/login/", data = {
        "email": "naoexiste@email.com",
        "senha": "123456"
    })
    assert response.status_code == 401
    data = response.get_json()
    assert "erro" in data