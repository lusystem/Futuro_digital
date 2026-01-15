from flask import Flask, Blueprint, request, jsonify
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from conf.database import db

aluno_bp = Blueprint('aluno', __name__, url_prefix = '/aluno')

@aluno_bp.route('/criar', methods=['POST'])
def cadastrar(): 
    nome = request.form.get('nome')
    pcd = request.form.get('pcd') == 'true' #boolean no banco de dados
    idade = request.form.get('idade')
    descricao_flag = request.form.get('descricao_flag')
    id_turma = request.form.get('id_turma')

    if not nome or not idade or not id_turma:
        return {'erro': 'Nome, idade e id_turma são obrigatórios.'}, 400
    
    try:
        id_turma = int(id_turma)
    except (ValueError, TypeError):
        return {'erro': 'id_turma deve ser um número inteiro.'}, 400
    
    try:
        idade = int(idade)
    except (ValueError, TypeError):
        return {'erro': 'idade deve ser um número inteiro.'}, 400
    
    turma = db.session.execute(text("SELECT capacidade_maxima FROM turmas WHERE id_turma = :id_turma"),
        {'id_turma': id_turma}).fetchone()

    if not turma:
        return {'erro': 'Turma não encontrada.'}, 404

    capacidade_maxima = turma[0]
    
    total_alunos = db.session.execute(text("SELECT COUNT(*) FROM alunos WHERE id_turma = :id_turma"),
        {'id_turma': id_turma}).scalar()
    
    if total_alunos >= capacidade_maxima:
        return {'erro': 'Turma lotada. Não há vagas disponíveis.'}, 400
    
    sql = text("""
               INSERT INTO alunos( nome, pcd, idade, descricao_flag, id_turma)
               VALUES (:nome, :pcd, :idade, :descricao_flag, :id_turma)
               RETURNING id_aluno
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
        id_aluno = result.fetchone()[0]
        db.session.commit()

        dados['id_aluno'] = id_aluno
        return dados, 201
    except Exception as e:
        db.session.rollback()
        return {'erro': str(e)}, 400

@aluno_bp.route('/atualizar/<int:id>', methods=['PUT'])
def atualizar(id):
    nome = request.form.get('nome')
    pcd = request.form.get('pcd') == 'true'  #boolean no banco de dados
    idade = request.form.get('idade')
    descricao_flag = request.form.get('descricao_flag')
    id_turma = request.form.get('id_turma')
    
    try:
        idade = int(idade) if idade else None
        id_turma = int(id_turma) if id_turma else None
    except (ValueError, TypeError):
        return {'erro': 'idade e id_turma devem ser números'}, 400
    
    sql = text("""
               UPDATE alunos
               SET nome = :nome,
                   pcd = :pcd,
                   idade = :idade,
                   descricao_flag = :descricao_flag,
                   id_turma = :id_turma
               WHERE id_aluno = :id
               RETURNING id_aluno
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
        result = db.session.execute(sql, dados)
        db.session.commit()
        id_aluno = result.fetchone()[0]
        return {
            'id_aluno': id_aluno,
            'nome': nome,
            'pcd': pcd,
            'idade': idade,
            'descricao_flag': descricao_flag,
            'id_turma': id_turma
        }, 200
    except Exception as e:
        db.session.rollback()
        return {'erro': str(e)}, 400

@aluno_bp.route('/deletar/<int:id>', methods=['DELETE'])
def deletar(id):
    sql = text("DELETE FROM alunos WHERE id_aluno = :id")
    dados = {'id': id}
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Aluno deletado com sucesso'}, 200
    except Exception as e:
        db.session.rollback()
        return {'erro': str(e)}, 400

@aluno_bp.route('/ver_uma/<int:id>', methods=['GET'])
def ver(id):
    sql = text("SELECT * FROM alunos WHERE id_aluno = :id")
    dados = {'id': id}
    try:
        result = db.session.execute(sql, dados)
        aluno = result.fetchone()
        if aluno:
            aluno_dict = {
                'id_aluno': aluno[0],
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