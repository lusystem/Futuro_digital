from flask import Flask
from conf.database import init_db
from flask_jwt_extended import JWTManager
from control.CRUD_Escolas import escola_bp
from control.CRUD_Turmas import turma_bp
from control.CRUD_Aluno import aluno_bp
from control.cadastro import cadastro_bp
from control.login import login_bp
from control.CRUD_Staff import staff_bp
from control.CRUD_Projetos import projetos_bp
from control.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'chave-mega-secreta'
    jwt = JWTManager(app)

    app.register_blueprint(escola_bp)
    app.register_blueprint(turma_bp)
    app.register_blueprint(aluno_bp)
    app.register_blueprint(cadastro_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(staff_bp)
    app.register_blueprint(projetos_bp)
    app.register_blueprint(dashboard_bp)

    init_db(app)

    @app.route("/")
    def home():
        return "API Gestao Educacional rodando!"
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)