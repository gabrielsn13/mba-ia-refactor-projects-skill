from functools import wraps

from flask import current_app, g, request
from itsdangerous import BadSignature, URLSafeTimedSerializer

from src.database.db import db
from src.middlewares.errors import ForbiddenError, UnauthorizedError
from src.models.user import User

# Endpoints acessiveis sem token.
PUBLIC_ENDPOINTS = {'index', 'health', 'auth.login', 'users.create_user', 'static'}

_SALT = 'task-manager-auth'


def _serializer():
    return URLSafeTimedSerializer(current_app.config['SECRET_KEY'], salt=_SALT)


def issue_token(user):
    return _serializer().dumps({'uid': user.id})


def _user_from_request():
    header = request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        return None
    try:
        payload = _serializer().loads(
            header[len('Bearer '):], max_age=current_app.config['TOKEN_MAX_AGE_SECONDS']
        )
    except BadSignature:
        return None
    user = db.session.get(User, payload.get('uid'))
    return user if user and user.active else None


def authenticate():
    """before_request: exige token valido fora dos endpoints publicos."""
    g.current_user = _user_from_request()
    if request.method == 'OPTIONS' or request.endpoint in PUBLIC_ENDPOINTS:
        return None
    if g.current_user is None:
        raise UnauthorizedError('Token ausente ou inválido')
    return None


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = g.get('current_user')
        if user is None or not user.is_admin():
            raise ForbiddenError('Acesso restrito a administradores')
        return fn(*args, **kwargs)
    return wrapper
