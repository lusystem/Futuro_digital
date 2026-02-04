#Banco de dados temporário para teste
import sys
import os
import pytest

os.environ["PYTHONUTF8"] = "1"

#Garante que o diretório raiz do projeto seja incluído no sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT_DIR)

from app import create_app
from conf.database import db
from sqlalchemy import text

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123@localhost/edugesto'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    with app.app_context():
        db.session.execute(text('DROP TABLE IF EXISTS projeto_professores CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS projetos CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS alunos CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS turmas CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS staff CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS escolas CASCADE'))
        db.session.execute(text('DROP TABLE IF EXISTS usuarios CASCADE'))
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
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS staff (
                id_staff SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                cargo TEXT NOT NULL,
                carga_horaria TEXT,
                especialidade TEXT,
                id_escola INTEGER NOT NULL,
                status_lotacao TEXT DEFAULT 'Efetivo',
                escola_origem_id INTEGER,
                FOREIGN KEY (id_escola) REFERENCES escolas(id_escola),
                FOREIGN KEY (escola_origem_id) REFERENCES escolas(id_escola)
            )
        """))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS projetos (
                id_projeto SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                data_inicio DATE NOT NULL,
                data_fim DATE NOT NULL,
                nivel TEXT NOT NULL,
                alunos_atingidos INTEGER DEFAULT 0
            )
        """))
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS projeto_professores (
                id_vinculo SERIAL PRIMARY KEY,
                id_projeto INTEGER NOT NULL,
                id_staff INTEGER NOT NULL,
                FOREIGN KEY (id_projeto) REFERENCES projetos(id_projeto),
                FOREIGN KEY (id_staff) REFERENCES staff(id_staff),
                UNIQUE(id_projeto, id_staff)
            )
        """))
        db.session.commit()

        yield app.test_client()

        db.session.execute(text('TRUNCATE TABLE escolas RESTART IDENTITY CASCADE'))
        db.session.execute(text("TRUNCATE TABLE turmas RESTART IDENTITY CASCADE"))
        db.session.execute(text("TRUNCATE TABLE alunos RESTART IDENTITY CASCADE"))
        db.session.execute(text("TRUNCATE TABLE usuarios RESTART IDENTITY CASCADE"))
        db.session.execute(text("TRUNCATE TABLE staff RESTART IDENTITY CASCADE"))
        db.session.execute(text("TRUNCATE TABLE projeto_professores RESTART IDENTITY CASCADE"))
        db.session.execute(text("TRUNCATE TABLE projetos RESTART IDENTITY CASCADE"))
        db.session.commit()
        db.session.remove()