from flask import Blueprint, jsonify

from src.controllers import category_controller as ctrl
from src.controllers.validators import get_json_body

bp = Blueprint('categories', __name__)


@bp.route('/categories', methods=['GET'])
def list_categories():
    return jsonify(ctrl.list_categories()), 200


@bp.route('/categories', methods=['POST'])
def create_category():
    return jsonify(ctrl.create_category(get_json_body())), 201


@bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    return jsonify(ctrl.update_category(cat_id, get_json_body())), 200


@bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    ctrl.delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
