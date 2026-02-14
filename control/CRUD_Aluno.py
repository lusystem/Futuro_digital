from flask import Flask, Blueprint, request, jsonify
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from conf.database import db
from flask_jwt_extended import jwt_required, get_jwt
from control.seguranca import admin_qualquer

aluno_bp = Blueprint('alunos', __name__, url_prefix = '/alunos')

def autorizar_escola(id_escola):
    claims = get_jwt()
    cargo = claims.get('cargo')
    if cargo == 'admin_secretaria':
        return None
    if cargo == 'admin_escola' and claims.get('id_escola') == id_escola:
        return None
    return {'erro': 'Acesso não autorizado.'}, 403

def obter_escola_por_turma(id_turma):
    row = db.session.execute(
        text("SELECT id_escola FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id_turma}).fetchone()
    return row.id_escola if row else None

@aluno_bp.route('/criar', methods=['POST'])
@jwt_required()
@admin_qualquer
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
    
    turma = db.session.execute(text("SELECT capacidade_maxima FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id_turma}).fetchone()

    if not turma:
        return {'erro': 'Turma não encontrada.'}, 404

    id_escola = obter_escola_por_turma(id_turma)
    auth = autorizar_escola(id_escola)
    if auth:
        return auth

    sql_capacidade = text("SELECT capacidade_maxima FROM turmas WHERE id_turma = :id_turma")
    capacidade = db.session.execute(sql_capacidade, {'id_turma': id_turma}).fetchone()[0]

    sql_ocupados = text("SELECT COUNT(*) FROM alunos WHERE id_turma = :id_turma")
    ocupados = db.session.execute(sql_ocupados, {'id_turma': id_turma}).fetchone()[0]

    if ocupados >= capacidade:
        return {
            'erro': 'Turma lotada. Não há vagas disponíveis.'
        }, 400
    capacidade_maxima = turma[0]

    total_alunos = db.session.execute(text("SELECT COUNT(*) FROM alunos WHERE id_turma = :id_turma"), {'id_turma': id_turma}).scalar()
    
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
@jwt_required()
@admin_qualquer
def atualizar(id):
    nome = request.form.get('nome')
    pcd = request.form.get('pcd') == 'true'  #boolean no banco de dados
    idade = request.form.get('idade')
    descricao_flag = request.form.get('descricao_flag')
    id_turma = request.form.get('id_turma')
    
    aluno = db.session.execute(text("SELECT * FROM alunos WHERE id_aluno = :id"), {'id': id}).fetchone()
    if not aluno:
        return {'erro': 'Aluno não encontrado.'}, 404

    try:
        idade = int(idade) if idade else aluno.idade
        id_turma = int(id_turma) if id_turma else aluno.id_turma
    except (ValueError, TypeError):
        return {'erro': 'idade e id_turma devem ser números'}, 400

    id_escola = obter_escola_por_turma(id_turma)
    auth = autorizar_escola(id_escola)
    if auth:
        return auth
    
    capacidade = db.session.execute(text("SELECT capacidade_maxima FROM turmas WHERE id_turma = :id"), {'id': id_turma}).scalar()

    if capacidade is None:
        return {'erro': 'Turma não encontrada.'}, 404

    total = db.session.execute(text("SELECT COUNT(*) FROM alunos WHERE id_turma = :id"),{'id': id_turma}).scalar()

    if total >= capacidade and id_turma != aluno.id_turma:
        return {'erro': 'Turma lotada. Não é possível transferir o aluno.'}, 400
    
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
@jwt_required()
@admin_qualquer
def deletar(id):
    aluno = db.session.execute(text("SELECT id_turma FROM alunos WHERE id_aluno = :id"), {'id': id}).fetchone()
    if not aluno:
        return {'erro': 'Aluno não encontrado.'}, 404

    id_escola = obter_escola_por_turma(aluno.id_turma)
    auth = autorizar_escola(id_escola)
    if auth:
        return auth

    sql = text("DELETE FROM alunos WHERE id_aluno = :id")
    dados = {'id': id}
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Aluno deletado com sucesso'}, 200
    except Exception as e:
        db.session.rollback()
        return {'erro': str(e)}, 400

@aluno_bp.route('/ver/<int:id>', methods=['GET'])
@jwt_required()
@admin_qualquer
def ver(id):
    sql = text("SELECT * FROM alunos WHERE id_aluno = :id")
    dados = {'id': id}
    try:
        result = db.session.execute(sql, dados)
        aluno = result.fetchone()
        if aluno:
            id_escola = obter_escola_por_turma(aluno[5])
            auth = autorizar_escola(id_escola)
            if auth:
                return auth
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
    
@aluno_bp.route('/listar', methods=['GET'])
@jwt_required()
@admin_qualquer
def listar():
    try:
        claims = get_jwt()
        cargo = claims.get('cargo')
        if cargo == 'admin_escola':
            result = db.session.execute(
                text("""
                    SELECT a.*
                    FROM alunos a
                    JOIN turmas t ON a.id_turma = t.id_turma
                    WHERE t.id_escola = :id_escola
                """),
                {'id_escola': claims.get('id_escola')}
            )
        else:
            result = db.session.execute(text("SELECT * FROM alunos"))
        alunos = result.fetchall()
        alunos_list = []
        for aluno in alunos:
            aluno_dict = {
                'id_aluno': aluno[0],
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