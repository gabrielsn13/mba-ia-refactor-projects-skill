from flask import Blueprint, jsonify

from src.controllers import auth_controller as ctrl
from src.controllers.validators import get_json_body

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST'])
def login():
    return jsonify(ctrl.login(get_json_body())), 200
