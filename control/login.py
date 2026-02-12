#rota de login para autenticação de usuários
from flask import Blueprint, request, jsonify
from conf.database import db
from sqlalchemy import text
from control import seguranca
from flask_jwt_extended import create_access_token

login_bp = Blueprint('login', __name__, url_prefix = '/login')

@login_bp.route('/', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not email or not senha:
        return {'erro': 'Email e senha são obrigatórios.'}, 400
    
    sql = text("""
               SELECT id_usuario, nome_usuario, email, cargo, id_escola, senha
               FROM usuarios
               WHERE email = :email
               """)
    result = db.session.execute(sql, {'email': email})
    usuario = result.fetchone()

    if not usuario:
        return {'erro': 'Credenciais inválidas.'}, 401

    if not seguranca.verificar_senha(senha, usuario.senha):
        return {'erro': 'Credenciais inválidas.'}, 401

    token = create_access_token(
        identity=str(usuario.id_usuario),
        additional_claims={
            'cargo': usuario.cargo,
            'id_escola': usuario.id_escola
        }
    )

    return {
        'access_token': token,
        'id_usuario': usuario.id_usuario,
        'nome_usuario': usuario.nome_usuario,
        'email': usuario.email,
        'cargo': usuario.cargo
    }, 200