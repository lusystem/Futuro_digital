from flask import Blueprint, request, jsonify
from sqlalchemy import text
from conf.database import db

turma_bp = Blueprint('turma', __name__, url_prefix='/turma')

@turma_bp.route('/criar', methods=['POST'])
def cadastrar():
    try:
        nome = request.form.get('nome')
        serie = request.form.get('serie')
        capacidade_maxima = int(request.form.get('capacidade_maxima'))
        id_escola = int(request.form.get('id_escola'))

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
def atualizar(id):
    try:
        turma = db.session.execute(text("SELECT * FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id}).fetchone()

        if not turma:
            return {'erro': 'Turma não encontrada.'}, 404

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
def deletar(id):
    try:
        turma = db.session.execute(text("SELECT * FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id}).fetchone()

        if not turma:
            return {'erro': 'Turma não encontrada.'}, 404

        db.session.execute(text("DELETE FROM alunos WHERE id_turma = :id_turma"), {'id_turma': id})
        db.session.execute(text("DELETE FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id})
        db.session.commit()

        return {'mensagem': 'Turma deletada com sucesso'}, 200

    except Exception as e:
        print("ERRO:", e)
        return {'erro': str(e)}, 400

@turma_bp.route('/ver_uma/<int:id>', methods=['GET'])
def ver(id):
    try:
        result = db.session.execute(text("SELECT * FROM turmas WHERE id_turma = :id_turma"), {'id_turma': id})
        turma = result.fetchone()

        if turma:
            turma_dict = dict(turma._mapping)
            return turma_dict, 200
        else:
            return {'erro': 'Turma não encontrada'}, 404

    except Exception as e:
        print("ERRO:", e)
        return {'erro': str(e)}, 400

@turma_bp.route('/ver', methods=['GET'])
def listar():
    try:
        result = db.session.execute(text("SELECT * FROM turmas"))
        turmas = result.fetchall()
        lista = [dict(t._mapping) for t in turmas]

        return jsonify(lista), 200

    except Exception as e:
        print("ERRO:", e)
        return {'erro': str(e)}, 400
    
#vagas restantes na turma
@turma_bp.route('/vagas_restantes/<int:id>', methods=['GET'])
def vagas_turma(id):
    turma = db.session.execute(text("SELECT capacidade_maxima FROM turmas WHERE id_turma = :id"), {'id': id}).fetchone()

    if not turma:
        return {'erro': 'Turma não encontrada.'}, 404

    ocupados = db.session.execute(
        text("SELECT COUNT(*) FROM alunos WHERE id_turma = :id"),
        {'id': id}
    ).scalar()

    vagas_restantes = turma.capacidade_maxima - ocupados

    return {
        'id_turma': id,
        'capacidade_maxima': turma.capacidade_maxima,
        'ocupados': ocupados,
        'vagas_restantes': vagas_restantes
    }, 200