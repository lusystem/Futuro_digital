from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    default_uri = 'postgresql+psycopg2://postgres:123@localhost/edugesto'
    app.config.setdefault('SQLALCHEMY_DATABASE_URI', default_uri)
    app.config.setdefault('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    db.init_app(app)