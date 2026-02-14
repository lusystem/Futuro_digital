#implementação de controle de segurança com autenticação e autorização usando MD5
import hashlib
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt

def hash_senha(senha: str) -> str:
    """Gera hash MD5 da senha"""
    return hashlib.md5(senha.encode("utf-8")).hexdigest()

def verificar_senha(senha_digitada: str, senha_hash: str) -> bool:
    """Verifica se a senha digitada corresponde ao hash armazenado"""
    return hash_senha(senha_digitada) == senha_hash

def secretaria_apenas(fn):
    """Decorador para proteger rotas que exigem admin_secretaria"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        cargo = claims.get('cargo')
        
        if cargo != 'admin_secretaria':
            return {'erro': 'Acesso negado. Apenas admin_secretaria pode acessar.'}, 403
        
        return fn(*args, **kwargs)
    return wrapper

def escola_apenas(fn):
    """Decorador para proteger rotas que exigem admin_escola"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        cargo = claims.get('cargo')
        
        if cargo != 'admin_escola':
            return {'erro': 'Acesso negado. Apenas admin_escola pode acessar.'}, 403
        
        return fn(*args, **kwargs)
    return wrapper

def admin_qualquer(fn):
    """Decorador para rotas que exigem ser admin (qualquer tipo)"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        cargo = claims.get('cargo')
        
        if cargo not in ['admin_secretaria', 'admin_escola']:
            return {'erro': 'Acesso negado. Você precisa ser um admin.'}, 403
        
        return fn(*args, **kwargs)
    return wrapper