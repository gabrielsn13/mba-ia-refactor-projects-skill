from datetime import timedelta

from sqlalchemy import case, func

from src.config.settings import CLOSED_STATUSES
from src.database.db import db
from src.middlewares.errors import NotFoundError
from src.models.category import Category
from src.models.task import Task
from src.models.user import User
from src.utils.time import utc_now

PRIORITY_LABELS = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}


def _rate(done, total):
    return round((done / total) * 100, 2) if total > 0 else 0


def summary_report():
    now = utc_now()
    status_counts = dict(db.session.query(Task.status, func.count(Task.id)).group_by(Task.status).all())
    priority_counts = dict(
        db.session.query(Task.priority, func.count(Task.id)).group_by(Task.priority).all()
    )

    overdue_tasks = Task.query.filter(
        Task.due_date < now, Task.status.notin_(CLOSED_STATUSES)
    ).order_by(Task.id).all()

    seven_days_ago = now - timedelta(days=7)
    recent_created = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(
        Task.status == 'done', Task.updated_at >= seven_days_ago
    ).count()

    done_case = func.sum(case((Task.status == 'done', 1), else_=0))
    per_user = {
        uid: (total, done or 0)
        for uid, total, done in db.session.query(
            Task.user_id, func.count(Task.id), done_case
        ).group_by(Task.user_id).all()
    }
    user_stats = []
    for u in User.query.order_by(User.id).all():
        total, done = per_user.get(u.id, (0, 0))
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': done,
            'completion_rate': _rate(done, total),
        })

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': sum(status_counts.values()),
            'total_users': User.query.count(),
            'total_categories': Category.query.count(),
        },
        'tasks_by_status': {
            s: status_counts.get(s, 0) for s in ('pending', 'in_progress', 'done', 'cancelled')
        },
        'tasks_by_priority': {
            label: priority_counts.get(p, 0) for p, label in PRIORITY_LABELS.items()
        },
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': t.id,
                    'title': t.title,
                    'due_date': str(t.due_date),
                    'days_overdue': (now - t.due_date).days,
                }
                for t in overdue_tasks
            ],
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_created,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    now = utc_now()
    total = len(tasks)
    count = lambda status: sum(1 for t in tasks if t.status == status)  # noqa: E731
    done = count('done')

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': count('pending'),
            'in_progress': count('in_progress'),
            'cancelled': count('cancelled'),
            'overdue': sum(1 for t in tasks if t.is_overdue(now)),
            'high_priority': sum(1 for t in tasks if t.priority <= 2),
            'completion_rate': _rate(done, total),
        },
    }
