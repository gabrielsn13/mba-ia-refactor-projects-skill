import logging

from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

from src.config.settings import CLOSED_STATUSES
from src.controllers import validators as v
from src.database.db import db
from src.middlewares.errors import AppError, NotFoundError
from src.models.category import Category
from src.models.task import Task
from src.models.user import User
from src.utils.time import utc_now

logger = logging.getLogger(__name__)


def _get_task_or_404(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    return task


def _check_user(user_id):
    if user_id and not db.session.get(User, user_id):
        raise NotFoundError('Usuário não encontrado')


def _check_category(category_id):
    if category_id and not db.session.get(Category, category_id):
        raise NotFoundError('Categoria não encontrada')


def _commit(error_message):
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        logger.exception(error_message)
        raise AppError(error_message, 500)


def list_tasks():
    now = utc_now()
    query = Task.query.options(joinedload(Task.user), joinedload(Task.category)).order_by(Task.id)
    pagination = v.get_pagination()
    if pagination:
        page, per_page = pagination
        query = query.limit(per_page).offset((page - 1) * per_page)

    result = []
    for t in query.all():
        data = t.to_dict()
        data['overdue'] = t.is_overdue(now)
        data['user_name'] = t.user.name if t.user else None
        data['category_name'] = t.category.name if t.category else None
        result.append(data)
    return result


def get_task(task_id):
    task = _get_task_or_404(task_id)
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def create_task(data):
    title = v.validate_title(data.get('title')) if data.get('title') else None
    if not title:
        raise AppError('Título é obrigatório')

    status = v.validate_status(data.get('status', 'pending'))
    priority = v.validate_priority(data.get('priority', 3))
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    _check_user(user_id)
    _check_category(category_id)

    task = Task(
        title=title,
        description=data.get('description', ''),
        status=status,
        priority=priority,
        user_id=user_id,
        category_id=category_id,
    )
    if data.get('due_date'):
        task.due_date = v.validate_due_date(
            data['due_date'], 'Formato de data inválido. Use YYYY-MM-DD')
    if data.get('tags'):
        task.tags = v.serialize_tags(data['tags'])

    db.session.add(task)
    _commit('Erro ao criar task')
    logger.info('Task criada: %s - %s', task.id, task.title)
    return task.to_dict()


def update_task(task_id, data):
    task = _get_task_or_404(task_id)

    if 'title' in data:
        task.title = v.validate_title(data['title'])
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = v.validate_status(data['status'])
    if 'priority' in data:
        task.priority = v.validate_priority(data['priority'])
    if 'user_id' in data:
        _check_user(data['user_id'])
        task.user_id = data['user_id']
    if 'category_id' in data:
        _check_category(data['category_id'])
        task.category_id = data['category_id']
    if 'due_date' in data:
        task.due_date = (
            v.validate_due_date(data['due_date'], 'Formato de data inválido')
            if data['due_date'] else None
        )
    if 'tags' in data:
        task.tags = v.serialize_tags(data['tags'])

    task.updated_at = utc_now()
    _commit('Erro ao atualizar')
    logger.info('Task atualizada: %s', task.id)
    return task.to_dict()


def delete_task(task_id):
    task = _get_task_or_404(task_id)
    db.session.delete(task)
    _commit('Erro ao deletar')
    logger.info('Task deletada: %s', task_id)


def search_tasks(args):
    query = Task.query
    text = args.get('q', '')
    if text:
        like = f'%{text}%'
        query = query.filter(or_(Task.title.like(like), Task.description.like(like)))
    if args.get('status'):
        query = query.filter(Task.status == args['status'])

    priority = v.parse_int_arg('priority', 'Prioridade inválida')
    if priority is not None:
        query = query.filter(Task.priority == priority)
    user_id = v.parse_int_arg('user_id', 'user_id inválido')
    if user_id is not None:
        query = query.filter(Task.user_id == user_id)

    return [t.to_dict() for t in query.order_by(Task.id).all()]


def task_stats():
    counts = dict(db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all())
    total = sum(counts.values())
    done = counts.get('done', 0)
    overdue = Task.query.filter(
        Task.due_date < utc_now(), Task.status.notin_(CLOSED_STATUSES)
    ).count()
    return {
        'total': total,
        'pending': counts.get('pending', 0),
        'in_progress': counts.get('in_progress', 0),
        'done': done,
        'cancelled': counts.get('cancelled', 0),
        'overdue': overdue,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }
