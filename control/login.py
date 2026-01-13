#rota de login
from flask import Blueprint, request, jsonify
from conf.database import db
from sqlalchemy import text

login_bp = Blueprint('login', __name__, url_prefix = '/login')

@login_bp.route('/', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not email or not senha:
        return {'erro': 'Email e senha são obrigatórios.'}, 400
    
    #verificar se esta no banco de dados
    sql = text("""
               SELECT id_usuario, nome_usuario, email, cargo, id_escola
               FROM usuarios
               WHERE email = :email AND senha = :senha
               """)
    dados = {
        'email': email,
        'senha': senha #implementar hash de senha em produção
    }

    try:
        result = db.session.execute(sql, dados)
        usuario = result.fetchone()
        if not usuario:
            return {'erro': 'Credenciais inválidas.'}, 401
        
        usuario_dict = {
            'id_usuario': usuario[0],
            'nome_usuario': usuario[1],
            'email': usuario[2],
            'cargo': usuario[3],
            'id_escola': usuario[4]
        }
        return usuario_dict, 200
    except Exception as e:
        return {'erro': str(e)}, 400