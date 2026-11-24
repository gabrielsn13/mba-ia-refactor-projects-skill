from flask import Blueprint, jsonify, request

from src.controllers import task_controller as ctrl
from src.controllers.validators import get_json_body

bp = Blueprint('tasks', __name__)


@bp.route('/tasks', methods=['GET'])
def list_tasks():
    return jsonify(ctrl.list_tasks()), 200


# Rotas estaticas antes das dinamicas (/tasks/<int:id>).
@bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    return jsonify(ctrl.search_tasks(request.args)), 200


@bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(ctrl.task_stats()), 200


@bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    return jsonify(ctrl.get_task(task_id)), 200


@bp.route('/tasks', methods=['POST'])
def create_task():
    return jsonify(ctrl.create_task(get_json_body())), 201


@bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    return jsonify(ctrl.update_task(task_id, get_json_body())), 200


@bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    ctrl.delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200
