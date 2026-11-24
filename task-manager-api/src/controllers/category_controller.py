import logging

from sqlalchemy import func

from src.controllers import validators as v
from src.database.db import db
from src.middlewares.errors import AppError, NotFoundError
from src.models.category import Category
from src.models.task import Task

logger = logging.getLogger(__name__)


def _get_category_or_404(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise NotFoundError('Categoria não encontrada')
    return cat


def _commit(error_message):
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception(error_message)
        raise AppError(error_message, 500)


def list_categories():
    counts = dict(
        db.session.query(Task.category_id, func.count(Task.id)).group_by(Task.category_id).all()
    )
    result = []
    for c in Category.query.order_by(Category.id).all():
        data = c.to_dict()
        data['task_count'] = counts.get(c.id, 0)
        result.append(data)
    return result


def create_category(data):
    name = data.get('name')
    if not name:
        raise AppError('Nome é obrigatório')
    color = data.get('color', '#000000')
    v.validate_color(color)

    category = Category(name=name, description=data.get('description', ''), color=color)
    db.session.add(category)
    _commit('Erro ao criar categoria')
    return category.to_dict()


def update_category(cat_id, data):
    cat = _get_category_or_404(cat_id)
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = v.validate_color(data['color'])
    _commit('Erro ao atualizar')
    return cat.to_dict()


def delete_category(cat_id):
    cat = _get_category_or_404(cat_id)
    Task.query.filter_by(category_id=cat_id).update({'category_id': None})
    db.session.delete(cat)
    _commit('Erro ao deletar')
