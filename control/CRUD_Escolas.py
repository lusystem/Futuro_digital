from flask import Flask, Blueprint, request, jsonify
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from conf.database import db

escola_bp = Blueprint('escola', __name__, url_prefix = '/escolas') 

@escola_bp.route('/criar', methods = ['POST'])
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
def ver(id):
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
def listar():
    sql = text("SELECT * FROM escolas")
    try:
        result = db.session.execute(sql)
        escolas = [dict(row._mapping) for row in result.fetchall()]
        return jsonify(escolas), 200
    except Exception as e:
        return {'erro': str(e)}, 400

@escola_bp.route('/<int:id>/vacancies', methods = ['GET'])
def calcular_vagas(id):
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