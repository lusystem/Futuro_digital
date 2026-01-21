from flask import Flask, Blueprint, request, jsonify
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import jwt_required
from conf.database import db
from control import seguranca

usuario_bp = Blueprint('usuario', __name__, url_prefix = '/usuarios')

@usuario_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def atualizar(id):
    nome_usuario = request.form.get('nome_usuario')
    email = request.form.get('email')
    senha = request.form.get('senha')
    cargo = request.form.get('cargo')
    id_escola = request.form.get('id_escola')
    
    senha_hash = seguranca.hash_senha(senha) if senha else None
    
    sql = text("""
               UPDATE usuarios
               SET nome_usuario = :nome_usuario,
                   email = :email,
                   senha = :senha,
                   cargo = :cargo,
                   id_escola = :id_escola
               WHERE id_usuario = :id
               """)
    dados = {
        'id': id,
        'nome_usuario': nome_usuario,
        'email': email,
        'senha': senha_hash,
        'cargo': cargo,
        'id_escola': id_escola
    }
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Usuário atualizado com sucesso.'}, 200
    except Exception as e:
        return {'erro': str(e)}, 400
    
@usuario_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def deletar(id):
    sql = text("DELETE FROM usuarios WHERE id_usuario = :id")
    dados = {
        'id': id
    }
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Usuário deletado com sucesso.'}, 200
    except Exception as e:
        return {'erro': str(e)}, 400
    
@usuario_bp.route('/', methods=['GET'])
@jwt_required()
def listar():
    sql = text("""
               SELECT id_usuario, nome_usuario, email, cargo, id_escola
               FROM usuarios
               """)
    try:
        result = db.session.execute(sql)
        usuarios = []
        for row in result.fetchall():
            usuario_dict = {
                'id_usuario': row[0],
                'nome_usuario': row[1],
                'email': row[2],
                'cargo': row[3],
                'id_escola': row[4]
            }
            usuarios.append(usuario_dict)
        return jsonify(usuarios), 200
    except Exception as e:
        return {'erro': str(e)}, 400
    
@usuario_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def ver(id):
    sql = text("""
               SELECT id_usuario, nome_usuario, email, cargo, id_escola
               FROM usuarios
               WHERE id_usuario = :id
               """)
    dados = {
        'id': id
    }
    try:
        result = db.session.execute(sql, dados)
        usuario = result.fetchone()
        if usuario:
            usuario_dict = {
                'id_usuario': usuario[0],
                'nome_usuario': usuario[1],
                'email': usuario[2],
                'cargo': usuario[3],
                'id_escola': usuario[4]
            }
            return usuario_dict, 200
        else:
            return {'erro': 'Usuário não encontrado.'}, 404
    except Exception as e:
        return {'erro': str(e)}, 400