from flask import Blueprint, jsonify

from src.controllers import report_controller as ctrl

bp = Blueprint('reports', __name__)


@bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return jsonify(ctrl.summary_report()), 200


@bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    return jsonify(ctrl.user_report(user_id)), 200
