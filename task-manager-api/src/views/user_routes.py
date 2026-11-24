from flask import Blueprint, jsonify

from src.controllers import user_controller as ctrl
from src.controllers.validators import get_json_body
from src.middlewares.auth import admin_required

bp = Blueprint('users', __name__)


@bp.route('/users', methods=['GET'])
def list_users():
    return jsonify(ctrl.list_users()), 200


@bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(ctrl.get_user(user_id)), 200


@bp.route('/users', methods=['POST'])
def create_user():
    return jsonify(ctrl.create_user(get_json_body())), 201


@bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    return jsonify(ctrl.update_user(user_id, get_json_body())), 200


@bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    ctrl.delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200


@bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def list_user_tasks(user_id):
    return jsonify(ctrl.list_user_tasks(user_id)), 200
