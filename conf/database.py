from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    # Não sobrescrever uma configuração já existente (por exemplo em testes).
    default_uri = 'postgresql+psycopg2://postgres:123@localhost/Banco de dados - EduGestao'
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', default_uri)

    db.init_app(app)