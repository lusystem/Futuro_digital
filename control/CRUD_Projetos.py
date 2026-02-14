from flask import Blueprint, request, jsonify
from sqlalchemy import text
from conf.database import db
from flask_jwt_extended import jwt_required
from control.seguranca import admin_qualquer

projetos_bp = Blueprint('projetos', __name__, url_prefix = '/projetos')

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
    sql = text("SELECT * FROM projetos")
    try:
        result = db.session.execute(sql)
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
    if not result.fetchone():
        return {'erro': 'Servidor não encontrado.'}, 404
    
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
    sql = text("""
        SELECT s.* FROM staff s
        JOIN projeto_professores pp ON s.id_staff = pp.id_staff
        WHERE pp.id_projeto = :id_projeto
    """)
    try:
        result = db.session.execute(sql, {'id_projeto': id_projeto})
        professores = [dict(row._mapping) for row in result.fetchall()]
        return jsonify(professores), 200
    
    except Exception as e:
        return {'erro': str(e)}, 400