#CRUD inicial de alunos
from flask import Flask, Blueprint, request, jsonify
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from conf.database import db

aluno_bp = Blueprint('aluno', __name__, url_prefix = '/alunos')

#Cadastrar um novo aluno
@aluno_bp.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    pcd = request.form.get('pcd')
    idade = request.form.get('idade')
    descricao_flag = request.form.get('descricao_flag')
    id_turma = request.form.get('id_turma')
    sql = text("""
               INSERT INTO alunos( nome, pcd, idade, descricao_flag, id_turma)
               VALUES (:nome, :idade, :descricao_flag, :id_turma)
               RETURNING id
               """)
    dados = {
        'nome': nome,
        'pcd': pcd,
        'idade': idade,
        'descricao_flag': descricao_flag,
        'id_turma': id_turma
    }
    
    try:
        result = db.session.execute(sql, dados)
        db.session.commit()
        id_gerado = result.fetchone()[0]
        dados['id'] = id_gerado
        return dados, 201
    except Exception as e:
        return {'erro': str(e)}, 400

#Atualizar um aluno existente
@aluno_bp.route('/<int:id>', methods=['PUT'])
def atualizar(id):
    nome = request.form.get('nome')
    pcd = request.form.get('pcd')
    idade = request.form.get('idade')
    descricao_flag = request.form.get('descricao_flag')
    id_turma = request.form.get('id_turma')
    sql = text("""
               UPDATE alunos
               SET nome = :nome,
                   pcd = :pcd,
                   idade = :idade,
                   descricao_flag = :descricao_flag,
                   id_turma = :id_turma
               WHERE id = :id
               """)
    dados = {
        'id': id,
        'nome': nome,
        'pcd': pcd,
        'idade': idade,
        'descricao_flag': descricao_flag,
        'id_turma': id_turma
    }

    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return dados, 200
    except Exception as e:
        return {'erro': str(e)}, 400

#Deletar um aluno existente
@aluno_bp.route('/<int:id>', methods=['DELETE'])
def deletar(id):
    sql = text("DELETE FROM alunos WHERE id = :id")
    dados = {'id': id}

    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Aluno deletado com sucesso.'}, 200
    except Exception as e:
        return {'erro': str(e)}, 400

#Ver aluno especifico
@aluno_bp.route('/<int:id>', methods=['GET'])
def ver(id):
    sql = text("SELECT * FROM alunos WHERE id = :id")
    dados = {'id': id}

    try:
        result = db.session.execute(sql, dados)
        aluno = result.fetchone()
        if aluno:
            aluno_dict = {
                'id': aluno[0],
                'nome': aluno[1],
                'pcd': aluno[2],
                'idade': aluno[3],
                'descricao_flag': aluno[4],
                'id_turma': aluno[5]
            }
            return aluno_dict, 200
        else:
            return {'mensagem': 'Aluno não encontrado.'}, 404
    except Exception as e:
        return {'erro': str(e)}, 400

#Listar todos os alunos
@aluno_bp.route('/ver', methods=['GET'])
def listar():
    sql = text("SELECT * FROM alunos")

    try:
        result = db.session.execute(sql)
        alunos = result.fetchall()
        alunos_list = []
        for aluno in alunos:
            aluno_dict = {
                'id': aluno[0],
                'nome': aluno[1],
                'pcd': aluno[2],
                'idade': aluno[3],
                'descricao_flag': aluno[4],
                'id_turma': aluno[5]
            }
            alunos_list.append(aluno_dict)
        return jsonify(alunos_list), 200
    except Exception as e:
        return {'erro': str(e)}, 400