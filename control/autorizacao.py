from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from functools import wraps

def admin_secretaria_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('cargo') != 'admin_secretaria':
            return {'erro': 'Acesso restrito à secretaria.'}, 403
        return fn(*args, **kwargs)
    return wrapper

def admin_escola_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('cargo') != 'admin_escola':
            return {'erro': 'Acesso restrito à escola.'}, 403
        return fn(*args, **kwargs)
    return wrapper