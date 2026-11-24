import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Erro de domínio traduzido para uma resposta JSON padronizada."""

    def __init__(self, message, status=400, sucesso=None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.sucesso = sucesso


class NotFoundError(AppError):
    def __init__(self, message, sucesso=None):
        super().__init__(message, 404, sucesso)


class UnauthorizedError(AppError):
    def __init__(self, message, sucesso=None):
        super().__init__(message, 401, sucesso)


class ForbiddenError(AppError):
    def __init__(self, message):
        super().__init__(message, 403)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        body = {"erro": error.message}
        if error.sucesso is not None:
            body["sucesso"] = error.sucesso
        return jsonify(body), error.status

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({"erro": error.description}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        logger.exception("Erro não tratado: %s", error)
        return jsonify({"erro": "Erro interno do servidor"}), 500
