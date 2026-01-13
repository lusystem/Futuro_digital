#CRUD inicial de escolas 
from flask import Flask, Blueprint, request, jsonify
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from conf.database import db

escola_bp = Blueprint('escola', __name__, url_prefix = '/escolas') 

#Cadastrar uma nova escola
@escola_bp.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    endereco = request.form.get('endereco')
    quantidade_turmas = request.form.get('quantidade_turmas')
    capacidade_alunos = request.form.get('capacidade_alunos')
    vagas = request.form.get('vagas')
    tipo = request.form.get('tipo')
    sql = text("""
               INSERT INTO escolas( nome, endereco, quantidade_turmas, 
               capacidade_alunos, vagas, tipo)
               VALUES (:nome, :endereco, :quantidade_turmas, 
               :capacidade_alunos, :vagas, :tipo)
               RETURNING id
               """)
    dados = {
        'nome': nome,
        'endereco': endereco,
        'quantidade_turmas': quantidade_turmas,
        'capacidade_alunos': capacidade_alunos,
        'vagas': vagas,
        'tipo': tipo
    }
    try:
        result = db.session.execute(sql, dados)
        db.session.commit()
        id_gerado = result.fetchone()[0]
        dados['id'] = id_gerado
        return dados, 201
    except Exception as e:
        return {'erro': str(e)}, 400
    
#Atualizar uma escola existente
@escola_bp.route('/<int:id>', methods=['PUT'])
def atualizar(id):
    nome = request.form.get('nome')
    endereco = request.form.get('endereco')
    quantidade_turmas = request.form.get('quantidade_turmas')
    capacidade_alunos = request.form.get('capacidade_alunos')
    vagas = request.form.get('vagas')
    tipo = request.form.get('tipo')
    sql = text("""
               UPDATE escolas
               SET nome = :nome,
                   endereco = :endereco,
                   quantidade_turmas = :quantidade_turmas,
                   capacidade_alunos = :capacidade_alunos,
                   vagas = :vagas,
                   tipo = :tipo
               WHERE id = :id
               """)
    dados = {
        'id': id,
        'nome': nome,
        'endereco': endereco,
        'quantidade_turmas': quantidade_turmas,
        'capacidade_alunos': capacidade_alunos,
        'vagas': vagas,
        'tipo': tipo
    }
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return dados, 200
    except Exception as e:
        return {'erro': str(e)}, 400

#Deletar uma escola existente
@escola_bp.route('/<int:id>', methods=['DELETE'])
def deletar(id):
    sql = text("DELETE FROM escolas WHERE id = :id")
    dados = {'id': id}
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Escola deletada com sucesso.'}, 200
    except Exception as e:
        return {'erro': str(e)}, 400

#Ver escola especifica
@escola_bp.route('/<int:id>', methods=['GET'])
def ver(id):
    sql = text("SELECT * FROM escolas WHERE id = :id")
    dados = {'id': id}
    try:
        result = db.session.execute(sql, dados)
        escola = result.fetchone()
        if escola:
            escola_dict = dict(escola)
            return escola_dict, 200
        else:
            return {'erro': 'Escola não encontrada.'}, 404
    except Exception as e:
        return {'erro': str(e)}, 400

#Listar todas as escolas
@escola_bp.route('/ver', methods=['GET'])
def listar():
    sql = text("SELECT * FROM escolas")
    try:
        result = db.session.execute(sql)
        escolas = [dict(row) for row in result.fetchall()]
        return jsonify(escolas), 200
    except Exception as e:
        return {'erro': str(e)}, 400