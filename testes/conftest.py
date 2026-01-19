#Banco de dados temporário para testes
import sys
import os
import pytest

#Garante que o diretório raiz do projeto seja incluído no sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from app import app
from conf.database import db, init_db
from sqlalchemy import text

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('TEST_DATABASE_URI', 'postgresql+psycopg2://postgres:123@localhost:5432/gestao_testes')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if 'sqlalchemy' not in getattr(app, 'extensions', {}):
        init_db(app)

    with app.app_context():
        if 'sqlalchemy' not in getattr(app, 'extensions', {}):
            init_db(app)

        db.session.execute(text('DROP TABLE IF EXISTS alunos CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS turmas CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS escolas CASCADE'))
        db.session.commit()

        db.session.execute(text('''
            CREATE TABLE IF NOT EXISTS escolas (
                id_escola SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                endereco TEXT NOT NULL,
                tipo TEXT NOT NULL,
                quantidade_turmas INTEGER NOT NULL,
                vagas INTEGER NOT NULL,
                capacidade_alunos INTEGER NOT NULL
            )
        '''))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS turmas (
                id_turma SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                serie TEXT NOT NULL,
                capacidade_maxima INTEGER NOT NULL,
                id_escola INTEGER NOT NULL,
                FOREIGN KEY (id_escola) REFERENCES escolas(id_escola)
            )
        """))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS alunos (
                id_aluno SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                pcd BOOLEAN DEFAULT FALSE,
                idade INTEGER,
                descricao_flag TEXT,
                id_turma INTEGER,
                FOREIGN KEY (id_turma) REFERENCES turmas(id_turma)
            )
        """))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario SERIAL PRIMARY KEY,
                nome_usuario TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                cargo TEXT NOT NULL,
                id_escola INTEGER,
                FOREIGN KEY (id_escola) REFERENCES escolas(id_escola)
            )
        """))
        db.session.commit()

        yield app.test_client()

        db.session.execute(text('TRUNCATE TABLE escolas RESTART IDENTITY CASCADE'))
        db.session.execute(text("TRUNCATE TABLE turmas RESTART IDENTITY CASCADE"))
        db.session.execute(text("TRUNCATE TABLE escolas RESTART IDENTITY CASCADE"))
        db.session.execute(text("TRUNCATE TABLE usuarios RESTART IDENTITY CASCADE"))
        db.session.commit()
        db.session.remove()