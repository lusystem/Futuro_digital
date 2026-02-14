from flask import Blueprint, request, jsonify
from sqlalchemy import text
from conf.database import db
from flask_jwt_extended import jwt_required, get_jwt
from control.seguranca import admin_qualquer

turma_bp = Blueprint('turmas', __name__, url_prefix='/turmas')

def autorizar_escola(id_escola):
    claims = get_jwt()
    cargo = claims.get('cargo')
    if cargo == 'admin_secretaria':
        return None
    if cargo == 'admin_escola' and claims.get('id_escola') == id_escola:
        return None
    return {'erro': 'Acesso não autorizado.'}, 403

@turma_bp.route('/criar', methods=['POST'])
@jwt_required()
@admin_qualquer
def cadastrar():
    try:
        nome = request.form.get('nome')
        serie = request.form.get('serie')
        capacidade_maxima = int(request.form.get('capacidade_maxima'))
        id_escola = int(request.form.get('id_escola'))

        auth = autorizar_escola(id_escola)
        if auth:
            return auth

        escola = db.session.execute(text("SELECT * FROM escolas WHERE id_escola = :id_escola"), {'id_escola': id_escola}).fetchone()

        if not escola:
            return {'erro': 'Escola não encontrada.'}, 404
        
        sql = text("""
            INSERT INTO turmas (nome, serie, capacidade_maxima, id_escola)
            VALUES (:nome, :serie, :capacidade_maxima, :id_escola)
            RETURNING id_turma
        """)
        dados = {
            'nome': nome,
            'serie': serie,
            'capacidade_maxima': capacidade_maxima,
            'id_escola': id_escola
        }
        result = db.session.execute(sql, dados)
        id_turma = result.fetchone()[0]
        db.session.commit()
        dados['id_turma'] = id_turma
        return dados, 201

    except Exception as e:
        print("ERRO:", e)
        return {'erro': str(e)}, 400

@turma_bp.route('/atualizar/<int:id>', methods=['PUT'])
@jwt_required()
@admin_qualquer
def atualizar(id):
    try:
        turma = db.session.execute(text("SELECT * FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id}).fetchone()

        if not turma:
            return {'erro': 'Turma não encontrada.'}, 404

        auth = autorizar_escola(turma.id_escola)
        if auth:
            return auth

        nome = request.form.get('nome')
        serie = request.form.get('serie')
        capacidade_maxima = int(request.form.get('capacidade_maxima'))
        id_escola = int(request.form.get('id_escola'))
        
        sql = text("""
            UPDATE turmas
            SET nome = :nome,
                serie = :serie,
                capacidade_maxima = :capacidade_maxima,
                id_escola = :id_escola
            WHERE id_turma = :id_turma
        """)
        dados = {
            'id_turma': id,
            'nome': nome,
            'serie': serie,
            'capacidade_maxima': capacidade_maxima,
            'id_escola': id_escola
        }
        db.session.execute(sql, dados)
        db.session.commit()

        return dados, 200

    except Exception as e:
        print("ERRO:", e)

        return {'erro': str(e)}, 400

@turma_bp.route('/deletar/<int:id>', methods=['DELETE'])
@jwt_required()
@admin_qualquer
def deletar(id):
    try:
        turma = db.session.execute(text("SELECT * FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id}).fetchone()

        if not turma:
            return {'erro': 'Turma não encontrada.'}, 404

        auth = autorizar_escola(turma.id_escola)
        if auth:
            return auth

        db.session.execute(text("DELETE FROM alunos WHERE id_turma = :id_turma"), {'id_turma': id})
        db.session.execute(text("DELETE FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id})
        db.session.commit()

        return {'mensagem': 'Turma deletada com sucesso'}, 200

    except Exception as e:
        print("ERRO:", e)
        return {'erro': str(e)}, 400

@turma_bp.route('/ver/<int:id>', methods=['GET'])
@jwt_required()
@admin_qualquer
def ver(id):
    try:
        result = db.session.execute(text("SELECT * FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id})
        turma = result.fetchone()

        if turma:
            auth = autorizar_escola(turma.id_escola)
            if auth:
                return auth
            turma_dict = dict(turma._mapping)
            return turma_dict, 200
        else:
            return {'erro': 'Turma não encontrada'}, 404

    except Exception as e:
        print("ERRO:", e)
        return {'erro': str(e)}, 400

@turma_bp.route('/listar', methods=['GET'])
@jwt_required()
@admin_qualquer
def listar():
    try:
        claims = get_jwt()
        cargo = claims.get('cargo')
        if cargo == 'admin_escola':
            result = db.session.execute(
                text("SELECT * FROM turmas WHERE id_escola = :id_escola"), {'id_escola': claims.get('id_escola')})
        else:
            result = db.session.execute(text("SELECT * FROM turmas"))
        turmas = result.fetchall()
        lista = [dict(t._mapping) for t in turmas]

        return jsonify(lista), 200

    except Exception as e:
        print("ERRO:", e)
        return {'erro': str(e)}, 400
    
@turma_bp.route('/vagas_restantes/<int:id>', methods=['GET'])
@jwt_required()
@admin_qualquer
def vagas_turma(id):
    turma = db.session.execute(text("SELECT capacidade_maxima FROM turmas WHERE id_turma = :id"), {'id': id}).fetchone()

    if not turma:
        return {'erro': 'Turma não encontrada.'}, 404

    turma_escola = db.session.execute(text("SELECT id_escola FROM turmas WHERE id_turma = :id"), {'id': id}).fetchone()
    if turma_escola:
        auth = autorizar_escola(turma_escola.id_escola)
        if auth:
            return auth

    ocupados = db.session.execute(text("SELECT COUNT(*) FROM alunos WHERE id_turma = :id"), {'id': id}).scalar()

    vagas_restantes = turma.capacidade_maxima - ocupados

    return {
        'id_turma': id,
        'capacidade_maxima': turma.capacidade_maxima,
        'ocupados': ocupados,
        'vagas_restantes': vagas_restantes
    }, 200