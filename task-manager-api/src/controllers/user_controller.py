import logging

from flask import g
from sqlalchemy import func

from src.controllers import validators as v
from src.database.db import db
from src.middlewares.errors import AppError, ConflictError, ForbiddenError, NotFoundError
from src.models.task import Task
from src.models.user import User

logger = logging.getLogger(__name__)


def _get_user_or_404(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    return user


def _commit(error_message):
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception(error_message)
        raise AppError(error_message, 500)


def _is_admin(user):
    return user is not None and user.is_admin()


def list_users():
    counts = dict(db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all())
    result = []
    for u in User.query.order_by(User.id).all():
        data = u.to_dict()
        data['task_count'] = counts.get(u.id, 0)
        result.append(data)
    return result


def get_user(user_id):
    user = _get_user_or_404(user_id)
    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.id).all()
    data['tasks'] = [t.to_dict() for t in tasks]
    return data


def create_user(data):
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise AppError('Nome é obrigatório')
    if not email:
        raise AppError('Email é obrigatório')
    if not password:
        raise AppError('Senha é obrigatória')

    v.validate_email(email)
    v.validate_password(password, 'Senha deve ter no mínimo 4 caracteres')
    if User.query.filter_by(email=email).first():
        raise ConflictError('Email já cadastrado')
    v.validate_role(role)
    if role != 'user' and not _is_admin(g.get('current_user')):
        raise ForbiddenError('Apenas administradores podem definir o role')

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    _commit('Erro ao criar usuário')
    logger.info('Usuário criado: %s - %s', user.id, user.name)
    return user.to_dict()


def update_user(user_id, data):
    user = _get_user_or_404(user_id)
    actor = g.current_user
    if actor.id != user.id and not _is_admin(actor):
        raise ForbiddenError('Sem permissão para alterar este usuário')

    if 'name' in data:
        user.name = data['name']
    if 'email' in data:
        v.validate_email(data['email'])
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ConflictError('Email já cadastrado')
        user.email = data['email']
    if 'password' in data:
        v.validate_password(data['password'], 'Senha muito curta')
        user.set_password(data['password'])
    if 'role' in data:
        v.validate_role(data['role'])
        if not _is_admin(actor):
            raise ForbiddenError('Apenas administradores podem alterar o role')
        user.role = data['role']
    if 'active' in data:
        if not isinstance(data['active'], bool):
            raise AppError('Campo active deve ser booleano')
        if not _is_admin(actor):
            raise ForbiddenError('Apenas administradores podem alterar active')
        user.active = data['active']

    _commit('Erro ao atualizar')
    return user.to_dict()


def delete_user(user_id):
    user = _get_user_or_404(user_id)
    db.session.delete(user)  # cascade remove as tasks do usuario
    _commit('Erro ao deletar')
    logger.info('Usuário deletado: %s', user_id)


def list_user_tasks(user_id):
    _get_user_or_404(user_id)
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.id).all()
    return [t.to_summary_dict() for t in tasks]
