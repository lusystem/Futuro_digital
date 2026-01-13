#CRUD de turmas inicial
#Conectado ao banco de dados PostgreSQL
from flask import Flask, Blueprint, request, jsonify
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from conf.database import db

turma_bp = Blueprint('turma', __name__, url_prefix = '/turmas')


#Cadastrar uma nova turma
@turma_bp.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    serie = request.form.get('serie')
    capacidade_maxima = request.form.get('capacidade_maxima')
    id_escola = request.form.get('id_escola')
    sql = text("""
               INSERT INTO turmas( nome, serie, capacidade_maxima, id_escola)
               VALUES (:nome, :serie, :capacidade_maxima, :id_escola)
               RETURNING id_turma
               """)
    dados = {
        'nome': nome,
        'serie': serie,
        'capacidade_maxima': capacidade_maxima,
        'id_escola': id_escola
    }
    try:
        result = db.session.execute(sql, dados)
        db.session.commit()
        id_gerado = result.fetchone()[0]
        dados['id'] = id_gerado
        return dados, 201
    except Exception as e:
        return {'erro': str(e)}, 400

#Atualizar uma turma existente
@turma_bp.route('/<int:id>', methods=['PUT'])
def atualizar(id):
    nome = request.form.get('nome')
    serie = request.form.get('serie')
    capacidade_maxima = request.form.get('capacidade_maxima')
    id_escola = request.form.get('id_escola')
    sql = text("""
               UPDATE turmas
               SET nome = :nome,
                   serie = :serie,
                   capacidade_maxima = :capacidade_maxima,
                   id_escola = :id_escola
               WHERE id_turma = :id
               """)
    dados = {
        'id': id,
        'nome': nome,
        'serie': serie,
        'capacidade_maxima': capacidade_maxima,
        'id_escola': id_escola
    }
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return dados, 200
    except Exception as e:
        return {'erro': str(e)}, 400

#Deletar uma turma existente
@turma_bp.route('/<int:id>', methods=['DELETE'])
def deletar(id):
    sql = text("DELETE FROM turmas WHERE id_turma = :id")
    dados = {'id': id}
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Turma deletada com sucesso'}, 200
    except Exception as e:
        return {'erro': str(e)}, 400

#Ver turma especifica
@turma_bp.route('/<int:id>', methods=['GET'])
def ver(id):
    sql = text("SELECT * FROM turmas WHERE id_turma = :id")
    dados = {'id': id}
    try:
        result = db.session.execute(sql, dados)
        turma = result.fetchone()
        if turma:
            turma_dict = {
                'id': turma[0],
                'nome': turma[1],
                'serie': turma[2],
                'capacidade_maxima': turma[3],
                'id_escola': turma[4]
            }
            return turma_dict, 200
        else:
            return {'erro': 'Turma não encontrada'}, 404
    except Exception as e:
        return {'erro': str(e)}, 400

#Listar todas as turmas
@turma_bp.route('/ver', methods=['GET'])
def listar():
    sql = text("SELECT * FROM turmas")
    try:
        result = db.session.execute(sql)
        turmas = result.fetchall()
        turmas_list = []
        for turma in turmas:
            turma_dict = {
                'id': turma[0],
                'nome': turma[1],
                'serie': turma[2],
                'capacidade_maxima': turma[3],
                'id_escola': turma[4]
            }
            turmas_list.append(turma_dict)
        return jsonify(turmas_list), 200
    except Exception as e:
        return {'erro': str(e)}, 400