from src.database.db import db
from src.middlewares.auth import issue_token
from src.middlewares.errors import AppError, ForbiddenError, UnauthorizedError
from src.models.user import User


def login(data):
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise AppError('Email e senha são obrigatórios')
    if not isinstance(email, str) or not isinstance(password, str):
        raise AppError('Email e senha são obrigatórios')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        db.session.rollback()
        raise UnauthorizedError('Credenciais inválidas')
    if not user.active:
        raise ForbiddenError('Usuário inativo')

    db.session.commit()  # persiste a migracao de hash legado, se houve
    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': issue_token(user),
    }
