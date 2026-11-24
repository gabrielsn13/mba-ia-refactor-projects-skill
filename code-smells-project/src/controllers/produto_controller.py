import logging

from flask import jsonify, request

from src.controllers.validators import validar_produto
from src.middlewares.error_handler import AppError, NotFoundError
from src.models import produto_model

logger = logging.getLogger(__name__)


def listar_produtos():
    produtos = produto_model.listar()
    logger.info("Listando %d produtos", len(produtos))
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar_produto(produto_id):
    produto = produto_model.buscar_por_id(produto_id)
    if not produto:
        raise NotFoundError("Produto não encontrado", sucesso=False)
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    campos = validar_produto(request.get_json(silent=True))
    produto_id = produto_model.criar(**campos)
    logger.info("Produto criado com ID: %s", produto_id)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(produto_id):
    if not produto_model.buscar_por_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    campos = validar_produto(request.get_json(silent=True))
    produto_model.atualizar(produto_id, **campos)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(produto_id):
    if not produto_model.buscar_por_id(produto_id):
        raise NotFoundError("Produto não encontrado")
    produto_model.deletar(produto_id)
    logger.info("Produto %s deletado", produto_id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    try:
        preco_min = float(request.args["preco_min"]) if request.args.get("preco_min") else None
        preco_max = float(request.args["preco_max"]) if request.args.get("preco_max") else None
    except ValueError:
        raise AppError("preco_min e preco_max devem ser numéricos")

    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
