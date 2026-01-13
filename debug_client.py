from app import app
from conf.database import init_db, db
from sqlalchemy import text

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
init_db(app)

with app.app_context():
    db.create_all()
    db.session.execute(text('''
        CREATE TABLE IF NOT EXISTS escolas (
            id_escola INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            endereco TEXT,
            tipo TEXT,
            quantidade_turmas INTEGER,
            vagas INTEGER,
            capacidade_alunos INTEGER
        )
    '''))
    db.session.commit()

    client = app.test_client()
    resp = client.post('/escolas', json={
        'nome': 'Escola Debug',
        'endereco': 'Rua Debug',
        'tipo': 'Publica',
        'quantidade_turmas': 1,
        'vagas': 10,
        'capacidade_alunos': 20
    })
    print('status:', resp.status_code)
    try:
        print('json:', resp.get_json())
    except Exception:
        print('data:', resp.data)
    # Testar GET por id e listar
    get_resp = client.get('/escolas/1')
    print('/escolas/1 ->', get_resp.status_code, get_resp.get_json())
    list_resp = client.get('/escolas')
    print('/escolas ->', list_resp.status_code, list_resp.get_json())

    # Mostrar logs de erros se houver
    
