import re

from flask import current_app, request

from src.config.settings import (
    COLOR_REGEX, EMAIL_REGEX, MAX_PRIORITY, MAX_TITLE_LENGTH, MIN_PASSWORD_LENGTH,
    MIN_PRIORITY, MIN_TITLE_LENGTH, VALID_ROLES, VALID_STATUSES,
)
from src.middlewares.errors import AppError
from src.utils.time import parse_date


def get_json_body():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        raise AppError('Dados inválidos')
    return data


def validate_title(title):
    if not isinstance(title, str):
        raise AppError('Título inválido')
    if len(title) < MIN_TITLE_LENGTH:
        raise AppError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise AppError('Título muito longo')
    return title


def validate_status(status):
    if status not in VALID_STATUSES:
        raise AppError('Status inválido')
    return status


def validate_priority(priority):
    if isinstance(priority, bool) or not isinstance(priority, int) \
            or priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise AppError('Prioridade deve ser entre 1 e 5')
    return priority


def validate_due_date(value, message):
    try:
        return parse_date(value)
    except ValueError:
        raise AppError(message)


def serialize_tags(tags):
    if isinstance(tags, list):
        if not all(isinstance(t, str) for t in tags):
            raise AppError('Tags inválidas')
        return ','.join(tags)
    if tags is None or isinstance(tags, str):
        return tags
    raise AppError('Tags inválidas')


def validate_email(email):
    if not isinstance(email, str) or not re.match(EMAIL_REGEX, email):
        raise AppError('Email inválido')
    return email


def validate_password(password, message):
    if not isinstance(password, str) or len(password) < MIN_PASSWORD_LENGTH:
        raise AppError(message)
    return password


def validate_role(role):
    if role not in VALID_ROLES:
        raise AppError('Role inválido')
    return role


def validate_color(color):
    if not isinstance(color, str) or not re.match(COLOR_REGEX, color):
        raise AppError('Cor inválida. Use o formato #RRGGBB')
    return color


def parse_int_arg(name, message):
    raw = request.args.get(name, '')
    if raw == '':
        return None
    try:
        return int(raw)
    except ValueError:
        raise AppError(message)


def get_pagination():
    """Retorna (page, per_page) ou None quando a paginacao nao foi pedida."""
    if 'page' not in request.args and 'per_page' not in request.args:
        return None
    page = parse_int_arg('page', 'Parâmetro page inválido') or 1
    per_page = parse_int_arg('per_page', 'Parâmetro per_page inválido') or 20
    if page < 1 or per_page < 1:
        raise AppError('Parâmetros de paginação inválidos')
    return page, min(per_page, current_app.config['MAX_PAGE_SIZE'])
