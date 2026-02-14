#rota de cadastro
from flask import Blueprint, request, jsonify
from conf.database import db
from sqlalchemy import text
from control import seguranca

cadastro_bp = Blueprint('cadastro', __name__, url_prefix = '/cadastro')

@cadastro_bp.route('/', methods=['POST'])
def cadastro():
    nome_usuario = request.form.get('nome_usuario')
    email = request.form.get('email')
    senha = request.form.get('senha')
    cargo = request.form.get('cargo')
    id_escola = request.form.get('id_escola')

    if not nome_usuario or not email or not senha:
        return {'erro': 'Todos os campos são obrigatórios.'}, 400

    senha = seguranca.hash_senha(senha)

    sql = text("""
               INSERT INTO usuarios( nome_usuario, email, senha, cargo, id_escola)
               VALUES (:nome_usuario, :email, :senha, :cargo, :id_escola)
               RETURNING id_usuario
               """)
    dados = {
        'nome_usuario': nome_usuario,
        'email': email,
        'senha': senha,
        'cargo': cargo,
        'id_escola': id_escola
    }
    try:
        result = db.session.execute(sql, dados)
        db.session.commit()
        id_gerado = result.fetchone()[0]
        return {
            'id_usuario': id_gerado,
            'nome_usuario': nome_usuario,
            'email': email,
            'cargo': cargo,
            'id_escola': id_escola
        }, 201
    except Exception as e:
        return {'erro': str(e)}, 400