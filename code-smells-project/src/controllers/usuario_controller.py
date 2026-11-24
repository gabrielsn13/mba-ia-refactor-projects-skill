import logging
import re

from flask import jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from src.middlewares.error_handler import AppError, NotFoundError, UnauthorizedError
from src.models import usuario_model

logger = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def listar_usuarios():
    return jsonify({"dados": usuario_model.listar(), "sucesso": True}), 200


def buscar_usuario(usuario_id):
    usuario = usuario_model.buscar_por_id(usuario_id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    dados = request.get_json(silent=True)
    if not dados:
        raise AppError("Dados inválidos")

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not nome or not email or not senha:
        raise AppError("Nome, email e senha são obrigatórios")
    if not EMAIL_REGEX.match(str(email)):
        raise AppError("Email inválido")

    usuario_id = usuario_model.criar(nome, email, generate_password_hash(str(senha)))
    logger.info("Usuário criado: id=%s", usuario_id)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    dados = request.get_json(silent=True) or {}
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        raise AppError("Email e senha são obrigatórios")

    usuario = usuario_model.buscar_com_senha_por_email(email)
    if not usuario or not check_password_hash(usuario["senha"], str(senha)):
        logger.warning("Login falhou para usuario")
        raise UnauthorizedError("Email ou senha inválidos", sucesso=False)

    logger.info("Login bem-sucedido: id=%s", usuario["id"])
    publico = {k: usuario[k] for k in ("id", "nome", "email", "tipo")}
    return jsonify({"dados": publico, "sucesso": True, "mensagem": "Login OK"}), 200
