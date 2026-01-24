from flask import Blueprint
from sqlalchemy import text
from conf.database import db
from flask_jwt_extended import jwt_required, get_jwt

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/general', methods = ['GET'])
@jwt_required()
def dashboard_geral():
    claims = get_jwt()
    cargo = claims.get('cargo')

    if cargo == 'admin_escola':
        return _dashboard_escola(claims.get('id_escola'))

    if cargo != 'admin_secretaria':
        return {'erro': 'Acesso não autorizado'}, 403

    try:
        row = db.session.execute(text("SELECT COUNT(*) FROM alunos")).fetchone() #Total de alunos
        total_alunos = row[0] if row else 0

        row = db.session.execute(text("SELECT SUM(capacidade_alunos) FROM escolas")).fetchone() #Capacidade total de alunos nas escolas
        total_capacidade = row[0] or 0

        row = db.session.execute(text("SELECT COUNT(*) FROM projetos WHERE data_fim >= CURRENT_DATE")).fetchone() #Projetos ativos
        total_projetos = row[0] if row else 0

        row = db.session.execute(text("SELECT SUM(alunos_atingidos) FROM projetos WHERE data_fim >= CURRENT_DATE")).fetchone() #Alunos atingidos por projetos
        alunos_projetos = row[0]

        result = db.session.execute(text("SELECT cargo, COUNT(*) FROM staff GROUP BY cargo")) #Servidores por cargo
        servidores = {r.cargo: r.total for r in result.fetchall()}

        total_escolas = db.session.execute(text("SELECT COUNT(*) FROM escolas")).fetchone()[0] #Total de escolas

        total_turmas = db.session.execute(text("SELECT COUNT(*) FROM turmas")).fetchone()[0] #Total de turmas

        percentual_ocupacao = round((total_alunos / total_capacidade) * 100, 2) if total_capacidade > 0 else 0 #Percentual de ocupação

        return {
            "tipo": "secretaria",
            "data_consolidacao": str(
                db.session.execute(text("SELECT CURRENT_DATE")).fetchone()[0]
            ),
            "cards": {
                "escolas": total_escolas,
                "turmas": total_turmas,
                "alunos": total_alunos,
                "vagas_ociosas": max(0, total_capacidade - total_alunos),
                "ocupacao_percentual": percentual_ocupacao,
                "projetos_ativos": total_projetos
            },
            "graficos": {
                "servidores_por_cargo": servidores,
                "alunos_em_projetos": alunos_projetos
            }
        }, 200

    except Exception as e:
        return {"erro": str(e)}, 500

def _dashboard_escola(id_escola):
    try:
        row = db.session.execute(
            text("SELECT COUNT(a.id_aluno) FROM alunos a JOIN turmas t ON a.id_turma = t.id_turma WHERE t.id_escola = :id"),
            {"id": id_escola}).fetchone()
        total_alunos = row[0] if row else 0

        row = db.session.execute(text("SELECT capacidade_alunos FROM escolas WHERE id_escola = :id"), {"id": id_escola}).fetchone()
        capacidade = row[0] if row else 0

        total_turmas = db.session.execute(text("SELECT COUNT(*) FROM turmas WHERE id_escola = :id"), {"id": id_escola}).fetchone()[0]

        result = db.session.execute(text("SELECT cargo, COUNT(*) total FROM staff WHERE id_escola = :id GROUP BY cargo"), {"id": id_escola})
        servidores = {r.cargo: r.total for r in result.fetchall()}

        projetos = db.session.execute(
            text("""
                SELECT COUNT(DISTINCT p.id_projeto)
                FROM projetos p
                JOIN projeto_professores pp ON p.id_projeto = pp.id_projeto
                JOIN staff s ON pp.id_staff = s.id_staff
                WHERE s.id_escola = :id
                AND p.data_fim >= CURRENT_DATE
            """), {"id": id_escola}).fetchone()[0]

        ocupacao = round((total_alunos / capacidade) * 100, 2) if capacidade > 0 else 0

        return {
            "tipo": "escola",
            "id_escola": id_escola,
            "cards": {
                "alunos": total_alunos,
                "vagas_ociosas": max(0, capacidade - total_alunos),
                "ocupacao_percentual": ocupacao,
                "turmas": total_turmas,
                "projetos_ativos": projetos
            },
            "graficos": {
                "servidores_por_cargo": servidores
            }
        }, 200
    except Exception as e:
        return {"erro": str(e)}, 500