from flask import Flask, Blueprint, request, jsonify
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from conf.database import db
from flask_jwt_extended import jwt_required, get_jwt
from control.seguranca import secretaria_apenas, admin_qualquer

escola_bp = Blueprint('escolas', __name__, url_prefix = '/escolas') 

def autorizar_escola(id_escola):
    claims = get_jwt()
    cargo = claims.get('cargo')
    if cargo == 'admin_secretaria':
        return None
    if cargo == 'admin_escola' and claims.get('id_escola') == id_escola:
        return None
    return {'erro': 'Acesso não autorizado.'}, 403

@escola_bp.route('/criar', methods = ['POST'])
@jwt_required()
@secretaria_apenas
def cadastrar():
    nome = request.form.get('nome')
    endereco = request.form.get('endereco')
    quantidade_turmas = int(request.form.get('quantidade_turmas'))
    capacidade_alunos = int(request.form.get('capacidade_alunos'))
    vagas = int(request.form.get('vagas'))
    tipo = request.form.get('tipo')
    sql = text("""
               INSERT INTO escolas( nome, endereco, quantidade_turmas, 
               capacidade_alunos, vagas, tipo)
               VALUES (:nome, :endereco, :quantidade_turmas, 
               :capacidade_alunos, :vagas, :tipo)
               RETURNING id_escola
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
        id_escola = result.fetchone()[0]
        db.session.commit()
        dados['id_escola'] = id_escola

        return dados, 201
    
    except Exception as e:
        return {'erro': str(e)}, 400
    
@escola_bp.route('/atualizar/<int:id>', methods = ['PUT'])
@jwt_required()
@secretaria_apenas
def atualizar(id):
    escola = db.session.execute(text("SELECT * FROM escolas WHERE id_escola = :id_escola"), {'id_escola': id}).fetchone()
    if not escola:
        return {'erro': 'Escola não encontrada.'}, 404
    
    nome = request.form.get('nome')
    endereco = request.form.get('endereco')
    quantidade_turmas = int(request.form.get('quantidade_turmas'))
    capacidade_alunos = int(request.form.get('capacidade_alunos'))
    vagas = int(request.form.get('vagas'))
    tipo = request.form.get('tipo')
    sql = text("""
               UPDATE escolas
               SET nome = :nome,
                   endereco = :endereco,
                   quantidade_turmas = :quantidade_turmas,
                   capacidade_alunos = :capacidade_alunos,
                   vagas = :vagas,
                   tipo = :tipo
               WHERE id_escola = :id_escola
               """)
    dados = {
        'id_escola': id,
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

@escola_bp.route('/deletar/<int:id>', methods = ['DELETE'])
@jwt_required()
@secretaria_apenas
def deletar(id):
    escola = db.session.execute(text("SELECT * FROM escolas WHERE id_escola = :id_escola"), {'id_escola': id}).fetchone()
    if not escola:
        return {'erro': 'Escola não encontrada.'}, 404
    
    sql = text("DELETE FROM escolas WHERE id_escola = :id_escola")
    dados = {'id_escola': id}
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Escola deletada com sucesso.'}, 200
    
    except Exception as e:
        return {'erro': str(e)}, 400

@escola_bp.route('/ver/<int:id>', methods = ['GET'])
@jwt_required()
@admin_qualquer
def ver(id):
    auth = autorizar_escola(id)
    if auth:
        return auth
    sql = text("SELECT * FROM escolas WHERE id_escola = :id_escola")
    dados = {'id_escola': id}
    try:
        result = db.session.execute(sql, dados)
        escola = result.fetchone()
        if escola:
            escola_dict = dict(escola._mapping)
            return escola_dict, 200
        else:
            return {'erro': 'Escola não encontrada.'}, 404
    except Exception as e:
        return {'erro': str(e)}, 400

@escola_bp.route('/listar', methods = ['GET'])
@jwt_required()
@admin_qualquer
def listar():
    claims = get_jwt()
    cargo = claims.get('cargo')
    if cargo == 'admin_escola':
        sql = text("SELECT * FROM escolas WHERE id_escola = :id_escola")
        params = {'id_escola': claims.get('id_escola')}
    else:
        sql = text("SELECT * FROM escolas")
        params = {}
    try:
        result = db.session.execute(sql, params)
        escolas = [dict(row._mapping) for row in result.fetchall()]
        return jsonify(escolas), 200
    except Exception as e:
        return {'erro': str(e)}, 400

@escola_bp.route('/<int:id>/vacancies', methods = ['GET'])
@jwt_required()
@admin_qualquer
def calcular_vagas(id):
    auth = autorizar_escola(id)
    if auth:
        return auth
    sql_escola = text("SELECT vagas, capacidade_alunos FROM escolas WHERE id_escola = :id_escola")
    try:
        result = db.session.execute(sql_escola, {'id_escola': id})
        escola = result.fetchone()
        
        if not escola:
            return {'erro': 'Escola não encontrada.'}, 404
        
        vagas_totais = escola.vagas
        
        #Contar alunos matriculados na escola
        sql_alunos = text("""
            SELECT COUNT(a.id_aluno) as total_alunos
            FROM alunos a
            JOIN turmas t ON a.id_turma = t.id_turma
            WHERE t.id_escola = :id_escola
        """)
        result_alunos = db.session.execute(sql_alunos, {'id_escola': id})
        alunos_row = result_alunos.fetchone()
        alunos_ocupados = alunos_row.total_alunos if alunos_row else 0
        
        vagas_livres = vagas_totais - alunos_ocupados
        
        return {
            'id_escola': id,
            'vagas_totais': vagas_totais,
            'vagas_ocupadas': alunos_ocupados,
            'vagas_livres': max(0, vagas_livres),
            'percentual_ocupacao': round((alunos_ocupados / vagas_totais * 100), 2) if vagas_totais > 0 else 0
        }, 200
        
    except Exception as e:
        return {'erro': str(e)}, 400