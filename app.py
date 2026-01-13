from flask import Flask
from conf.database import init_db
from control.CRUD_Escolas import escola_bp
from control.CRUD_Turmas import turma_bp
from control.CRUD_Aluno import aluno_bp
from control.cadastro import cadastro_bp
from control.login import login_bp

app = Flask(__name__)

# Nota: a inicialização do DB (`init_db`) é feita externamente (ex: em testes)
app.register_blueprint(escola_bp)
app.register_blueprint(turma_bp)
app.register_blueprint(aluno_bp)
app.register_blueprint(cadastro_bp)
app.register_blueprint(login_bp)

@app.route("/")
def home():
    return "API Gestao Educacional rodando!"

if __name__ == "__main__":
    app.run(debug=True)