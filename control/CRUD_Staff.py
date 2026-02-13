#CRUD de Staff (Servidores: Diretores, Professores, Orientadores)
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from conf.database import db
from flask_jwt_extended import jwt_required

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/criar', methods = ['POST'])
@jwt_required()
def criar_staff():
    nome = request.form.get('nome')
    cargo = request.form.get('cargo')
    carga_horaria = request.form.get('carga_horaria')
    especialidade = request.form.get('especialidade')
    id_escola = request.form.get('id_escola')
    status_lotacao = request.form.get('status_lotacao', 'Efetivo') 
    escola_origem_id = request.form.get('escola_origem_id')

    if not all([nome, cargo, carga_horaria, id_escola]):
        return {'erro': 'Nome, cargo, carga_horaria e id_escola são obrigatórios.'}, 400

    sql = text("""
        INSERT INTO staff (nome, cargo, carga_horaria, especialidade, id_escola, status_lotacao, escola_origem_id)
        VALUES (:nome, :cargo, :carga_horaria, :especialidade, :id_escola, :status_lotacao, :escola_origem_id)
        RETURNING id_staff
    """)
    dados = {
        'nome': nome,
        'cargo': cargo,
        'carga_horaria': carga_horaria,
        'especialidade': especialidade,
        'id_escola': id_escola,
        'status_lotacao': status_lotacao,
        'escola_origem_id': escola_origem_id
    }
    try:
        result = db.session.execute(sql, dados)
        id_staff = result.fetchone()[0]
        db.session.commit()
        
        dados['id_staff'] = id_staff
        return dados, 201
    
    except Exception as e:
        return {'erro': str(e)}, 400

@staff_bp.route('/ver/<int:id>', methods = ['GET'])
@jwt_required()
def ver_staff(id):
    sql = text("SELECT * FROM staff WHERE id_staff = :id_staff")
    
    try:
        result = db.session.execute(sql, {'id_staff': id})
        staff = result.fetchone()
        
        if staff:
            return dict(staff._mapping), 200
        else:
            return {'erro': 'Servidor não encontrado.'}, 404
    
    except Exception as e:
        return {'erro': str(e)}, 400

@staff_bp.route('/atualizar/<int:id>', methods = ['PUT'])
@jwt_required()
def atualizar_staff(id):
    sql_check = text("SELECT * FROM staff WHERE id_staff = :id_staff")
    result = db.session.execute(sql_check, {'id_staff': id})
    
    if not result.fetchone():
        return {'erro': 'Servidor não encontrado.'}, 404
    
    nome = request.form.get('nome')
    cargo = request.form.get('cargo')
    carga_horaria = request.form.get('carga_horaria')
    especialidade = request.form.get('especialidade')
    id_escola = request.form.get('id_escola')
    status_lotacao = request.form.get('status_lotacao')
    escola_origem_id = request.form.get('escola_origem_id')
    
    updates = []
    dados = {'id_staff': id}
    
    if nome:
        updates.append("nome = :nome")
        dados['nome'] = nome
    if cargo:
        updates.append("cargo = :cargo")
        dados['cargo'] = cargo
    if carga_horaria:
        updates.append("carga_horaria = :carga_horaria")
        dados['carga_horaria'] = carga_horaria
    if especialidade:
        updates.append("especialidade = :especialidade")
        dados['especialidade'] = especialidade
    if id_escola:
        updates.append("id_escola = :id_escola")
        dados['id_escola'] = id_escola
    if status_lotacao:
        updates.append("status_lotacao = :status_lotacao")
        dados['status_lotacao'] = status_lotacao
    if escola_origem_id:
        updates.append("escola_origem_id = :escola_origem_id")
        dados['escola_origem_id'] = escola_origem_id
    
    if not updates:
        return {'erro': 'Nenhum campo para atualizar.'}, 400
    
    sql = text(f"UPDATE staff SET {', '.join(updates)} WHERE id_staff = :id_staff")
    
    try:
        db.session.execute(sql, dados)
        db.session.commit()
        return {'mensagem': 'Servidor atualizado com sucesso.'}, 200
    
    except Exception as e:
        return {'erro': str(e)}, 400

@staff_bp.route('/deletar/<int:id>', methods = ['DELETE'])
@jwt_required()
def deletar_staff(id):
    sql_check = text("SELECT * FROM staff WHERE id_staff = :id_staff")
    result = db.session.execute(sql_check, {'id_staff': id})
    
    if not result.fetchone():
        return {'erro': 'Servidor não encontrado.'}, 404
    
    sql = text("DELETE FROM staff WHERE id_staff = :id_staff")
    
    try:
        db.session.execute(sql, {'id_staff': id})
        db.session.commit()
        return {'mensagem': 'Servidor deletado com sucesso.'}, 200
    
    except Exception as e:
        return {'erro': str(e)}, 400

@staff_bp.route('/listar', methods = ['GET'])
@jwt_required()
def listar_staff():
    papel = request.args.get('papel')
    especialidade = request.args.get('especialidade')
    escola = request.args.get('escola')
    status = request.args.get('status')
    
    sql = "SELECT * FROM staff WHERE 1=1"
    params = {}
    
    if papel:
        sql += " AND cargo = :papel"
        params['papel'] = papel
    
    if especialidade:
        sql += " AND especialidade = :especialidade"
        params['especialidade'] = especialidade
    
    if escola:
        sql += " AND id_escola = :escola"
        params['escola'] = escola
    
    if status:
        sql += " AND status_lotacao = :status"
        params['status'] = status
    
    try:
        result = db.session.execute(text(sql), params)
        staff_list = [dict(row._mapping) for row in result.fetchall()]
        return jsonify(staff_list), 200
    
    except Exception as e:
        return {'erro': str(e)}, 400