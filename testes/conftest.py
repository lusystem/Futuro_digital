#Banco de dados temporário para testes
import pytest
import sys
import os

# Garantir que o diretório raiz do projeto esteja no sys.path para importar `app`
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import app
from conf.database import db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    # Inicializar o DB após configurar a URI (evita depender de psycopg2 em ambiente de teste)
    from conf.database import init_db
    # Chamar init_db apenas se ainda não foi registrado no app
    if 'sqlalchemy' not in getattr(app, 'extensions', {}):
        init_db(app)

    with app.app_context():
        db.create_all()
        # Criar tabela `escolas` (DDL) para os testes, já que o projeto usa SQL cru
        from sqlalchemy import text
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
        yield app.test_client()
        db.session.remove()
        db.drop_all()