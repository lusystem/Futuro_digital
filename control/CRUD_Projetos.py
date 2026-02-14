from flask import Blueprint, request, jsonify
from sqlalchemy import text
from conf.database import db
from flask_jwt_extended import jwt_required, get_jwt
from control.seguranca import admin_qualquer

projetos_bp = Blueprint('projetos', __name__, url_prefix = '/projetos')

def _id_escola_admin_escola():
    claims = get_jwt()
    if claims.get('cargo') == 'admin_escola':
        return claims.get('id_escola')
    return None

def _autorizar_projeto_por_escola(id_projeto):
    id_escola_admin = _id_escola_admin_escola()
    if not id_escola_admin:
        return None
    row = db.session.execute(
        text("""
            SELECT 1
            FROM projeto_professores pp
            JOIN staff s ON s.id_staff = pp.id_staff
            WHERE pp.id_projeto = :id_projeto
              AND s.id_escola = :id_escola
            LIMIT 1
        """),
        {'id_projeto': id_projeto, 'id_escola': id_escola_admin}).fetchone()
    
    if row:
        return None
    return {'erro': 'Acesso não autorizado.'}, 403

@projetos_bp.route('/criar', methods = ['POST'])
@jwt_required()
@admin_qualquer
def criar_projeto():
    nome = request.form.get('nome')
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    nivel = request.form.get('nivel')
    alunos_atingidos = request.form.get('alunos_atingidos', 0)
    
    if not all([nome, data_inicio, data_fim, nivel]):
        return {'erro': 'Nome, data_inicio, data_fim e nivel são obrigatórios.'}, 400
    
    sql = text("""
        INSERT INTO projetos (nome, data_inicio, data_fim, nivel, alunos_atingidos)
        VALUES (:nome, :data_inicio, :data_fim, :nivel, :alunos_atingidos)
        RETURNING id_projeto
    """)
    dados = {
        'nome': nome,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'nivel': nivel,
        'alunos_atingidos': alunos_atingidos
    }
    try:
        result = db.session.execute(sql, dados)
        id_projeto = result.fetchone()[0]
        db.session.commit()
        dados['id_projeto'] = id_projeto
        return dados, 201
    
    except Exception as e:
        return {'erro': str(e)}, 400

@projetos_bp.route('/ver/<int:id>', methods = ['GET'])
@jwt_required()
@admin_qualquer
def ver_projeto(id):
    auth = _autorizar_projeto_por_escola(id)
    if auth:
        return auth
    sql = text("SELECT * FROM projetos WHERE id_projeto = :id_projeto")
    
    try:
        result = db.session.execute(sql, {'id_projeto': id})
        projeto = result.fetchone()
        
        if projeto:
            return dict(projeto._mapping), 200
        else:
            return {'erro': 'Projeto não encontrado.'}, 404
    
    except Exception as e:
        return {'erro': str(e)}, 400

@projetos_bp.route('/atualizar/<int:id>', methods = ['PUT'])
@jwt_required()
@admin_qualquer
def atualizar_projeto(id):
    auth = _autorizar_projeto_por_escola(id)
    if auth:
        return auth
    sql_check = text("SELECT * FROM projetos WHERE id_projeto = :id_projeto")
    result = db.session.execute(sql_check, {'id_projeto': id})
    
    if not result.fetchone():
        return {'erro': 'Projeto não encontrado.'}, 404
    
    nome = request.form.get('nome')
    data_inicio = request.form.get('data_inicio')
    data_fim = request.form.get('data_fim')
    nivel = request.form.get('nivel')
    alunos_atingidos = request.form.get('alunos_atingidos')
    updates = []
    dados = {'id_projeto': id}
    
    if nome:
        updates.append("nome = :nome")
        dados['nome'] = nome
    if data_inicio:
        updates.append("data_inicio = :data_inicio")
        dados['data_inicio'] = data_inicio
    if data_fim:
        updates.append("data_fim = :data_fim")
        dados['data_fim'] = data_fim
    if nivel:
        updates.append("nivel = :nivel")
        dados['nivel'] = nivel
    if alunos_atingidos:
        updates.append("alunos_atingidos = :alunos_atingidos")
        dados['alunos_atingidos'] = alunos_atingidos
    
    if not updates:
        return {'erro': 'Nenhum campo para atualizar.'}, 400
    
    sql = text(f"UPDATE projetos SET {', '.join(updates)} WHERE id_projeto = :id_projeto")
    
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Projeto atualizado com sucesso.'}, 200
    
    except Exception as e:
        return {'erro': str(e)}, 400

@projetos_bp.route('/deletar/<int:id>', methods = ['DELETE'])
@jwt_required()
@admin_qualquer
def deletar_projeto(id):
    auth = _autorizar_projeto_por_escola(id)
    if auth:
        return auth
    sql_check = text("SELECT * FROM projetos WHERE id_projeto = :id_projeto")
    result = db.session.execute(sql_check, {'id_projeto': id})
    
    if not result.fetchone():
        return {'erro': 'Projeto não encontrado.'}, 404
    
    sql = text("DELETE FROM projetos WHERE id_projeto = :id_projeto")
    
    try:
        db.session.execute(sql, {'id_projeto': id})
        db.session.commit()
        return {'mensagem': 'Projeto deletado com sucesso.'}, 200
    
    except Exception as e:
        return {'erro': str(e)}, 400

@projetos_bp.route('/listar', methods=['GET'])
@jwt_required()
@admin_qualquer
def listar_projetos():
    id_escola_admin = _id_escola_admin_escola()
    if id_escola_admin:
        sql = text("""
            SELECT DISTINCT p.*
            FROM projetos p
            JOIN projeto_professores pp ON p.id_projeto = pp.id_projeto
            JOIN staff s ON s.id_staff = pp.id_staff
            WHERE s.id_escola = :id_escola
        """)
        params = {'id_escola': id_escola_admin}
    else:
        sql = text("SELECT * FROM projetos")
        params = {}
    try:
        result = db.session.execute(sql, params)
        projetos_list = [dict(row._mapping) for row in result.fetchall()]
        return jsonify(projetos_list), 200
    
    except Exception as e:
        return {'erro': str(e)}, 400

@projetos_bp.route('/<int:id_projeto>/adicionar-professores', methods = ['POST'])
@jwt_required()
@admin_qualquer
def adicionar_professor_projeto(id_projeto):
    id_staff = request.form.get('id_staff')
    
    if not id_staff:
        return {'erro': 'id_staff é obrigatório.'}, 400
    
    sql_projeto = text("SELECT * FROM projetos WHERE id_projeto = :id_projeto")
    result = db.session.execute(sql_projeto, {'id_projeto': id_projeto})
    if not result.fetchone():
        return {'erro': 'Projeto não encontrado.'}, 404
    
    sql_staff = text("SELECT * FROM staff WHERE id_staff = :id_staff")
    result = db.session.execute(sql_staff, {'id_staff': id_staff})
    staff = result.fetchone()
    if not staff:
        return {'erro': 'Servidor não encontrado.'}, 404

    id_escola_admin = _id_escola_admin_escola()
    if id_escola_admin and staff.id_escola != id_escola_admin:
        return {'erro': 'Acesso não autorizado.'}, 403
    
    sql_check = text("""
        SELECT * FROM projeto_professores 
        WHERE id_projeto = :id_projeto AND id_staff = :id_staff
    """)
    result = db.session.execute(sql_check, {'id_projeto': id_projeto, 'id_staff': id_staff})
    if result.fetchone():
        return {'erro': 'Este professor já está vinculado a este projeto.'}, 400
    
    sql_count = text("""
        SELECT COUNT(*) as total FROM projeto_professores 
        WHERE id_projeto = :id_projeto
    """)
    result = db.session.execute(sql_count, {'id_projeto': id_projeto})
    count_row = result.fetchone()
    
    if count_row and count_row.total >= 5:
        return {'erro': 'Projeto já tem 5 professores vinculados (limite máximo).'}, 400
    
    sql = text("""
        INSERT INTO projeto_professores (id_projeto, id_staff)
        VALUES (:id_projeto, :id_staff)
        RETURNING id_vinculo
    """)
    try:
        result = db.session.execute(sql, {'id_projeto': id_projeto, 'id_staff': id_staff})
        id_vinculo = result.fetchone()[0]
        db.session.commit()
        return {
            'id_vinculo': id_vinculo,
            'id_projeto': id_projeto,
            'id_staff': id_staff,
            'mensagem': 'Professor vinculado com sucesso.'
        }, 201
    
    except Exception as e:
        return {'erro': str(e)}, 400

@projetos_bp.route('/<int:id_projeto>/remover-professor/<int:id_staff>', methods = ['DELETE'])
@jwt_required()
@admin_qualquer
def remover_professor_projeto(id_projeto, id_staff):
    id_escola_admin = _id_escola_admin_escola()
    if id_escola_admin:
        vinculo = db.session.execute(
            text("""
                SELECT 1
                FROM projeto_professores pp
                JOIN staff s ON s.id_staff = pp.id_staff
                WHERE pp.id_projeto = :id_projeto
                  AND pp.id_staff = :id_staff
                  AND s.id_escola = :id_escola
            """),
            {'id_projeto': id_projeto, 'id_staff': id_staff, 'id_escola': id_escola_admin}).fetchone()
        if not vinculo:
            return {'erro': 'Acesso não autorizado.'}, 403
    sql_check = text("""
        SELECT * FROM projeto_professores 
        WHERE id_projeto = :id_projeto AND id_staff = :id_staff
    """)
    result = db.session.execute(sql_check, {'id_projeto': id_projeto, 'id_staff': id_staff})
    
    if not result.fetchone():
        return {'erro': 'Vínculo não encontrado.'}, 404
    
    sql = text("""
        DELETE FROM projeto_professores 
        WHERE id_projeto = :id_projeto AND id_staff = :id_staff
    """)
    try:
        db.session.execute(sql, {'id_projeto': id_projeto, 'id_staff': id_staff})
        db.session.commit()
        return {'mensagem': 'Professor removido do projeto com sucesso.'}, 200
    
    except Exception as e:
        return {'erro': str(e)}, 400

@projetos_bp.route('/<int:id_projeto>/listar-professores', methods = ['GET'])
@jwt_required()
@admin_qualquer
def listar_professores_projeto(id_projeto):
    auth = _autorizar_projeto_por_escola(id_projeto)
    if auth:
        return auth

    id_escola_admin = _id_escola_admin_escola()
    if id_escola_admin:
        sql = text("""
            SELECT s.*
            FROM staff s
            JOIN projeto_professores pp ON s.id_staff = pp.id_staff
            WHERE pp.id_projeto = :id_projeto
              AND s.id_escola = :id_escola
        """)
        params = {'id_projeto': id_projeto, 'id_escola': id_escola_admin}
    else:
        sql = text("""
            SELECT s.*
            FROM staff s
            JOIN projeto_professores pp ON s.id_staff = pp.id_staff
            WHERE pp.id_projeto = :id_projeto
        """)
        params = {'id_projeto': id_projeto}
    try:
        result = db.session.execute(sql, params)
        professores = [dict(row._mapping) for row in result.fetchall()]
        return jsonify(professores), 200
    
    except Exception as e:
        return {'erro': str(e)}, 400