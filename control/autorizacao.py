from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps

def admin_secretaria_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_jwt_identity()
        if user['cargo'] != 'admin_secretaria':
            return {'erro': 'Acesso restrito à secretaria.'}, 403
        return fn(*args, **kwargs)
    return wrapper

def admin_escola_only(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = get_jwt_identity()
        if user['cargo'] != 'admin_escola':
            return {'erro': 'Acesso restrito à escola.'}, 403
        return fn(*args, **kwargs)
    return wrapper