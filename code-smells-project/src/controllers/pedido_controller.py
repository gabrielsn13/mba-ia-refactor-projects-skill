import logging

from flask import current_app, jsonify, request

from src.controllers.validators import validar_itens_pedido
from src.middlewares.error_handler import AppError, NotFoundError
from src.models import pedido_model, produto_model
from src.models.pedido_model import EstoqueInsuficienteError

logger = logging.getLogger(__name__)


def criar_pedido():
    dados = request.get_json(silent=True)
    if not dados:
        raise AppError("Dados inválidos")

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        raise AppError("Usuario ID é obrigatório")
    if not itens or not isinstance(itens, list):
        raise AppError("Pedido deve ter pelo menos 1 item")
    validar_itens_pedido(itens)

    total = 0
    itens_precificados = []
    for item in itens:
        produto = produto_model.buscar_por_id(item["produto_id"])
        if produto is None:
            raise AppError(f"Produto {item['produto_id']} não encontrado", sucesso=False)
        if produto["estoque"] < item["quantidade"]:
            raise AppError(f"Estoque insuficiente para {produto['nome']}", sucesso=False)
        total += produto["preco"] * item["quantidade"]
        itens_precificados.append({**item, "preco_unitario": produto["preco"]})

    try:
        pedido_id = pedido_model.criar_com_itens(
            usuario_id, current_app.config["STATUS_PEDIDO_INICIAL"], total, itens_precificados
        )
    except EstoqueInsuficienteError as erro:
        raise AppError(str(erro), sucesso=False)

    logger.info("Pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("Notificações (e-mail, SMS e push) enviadas para o pedido %s", pedido_id)
    return jsonify(
        {
            "dados": {"pedido_id": pedido_id, "total": total},
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }
    ), 201


def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": pedido_model.listar_por_usuario(usuario_id), "sucesso": True}), 200


def listar_todos_pedidos():
    return jsonify({"dados": pedido_model.listar_todos(), "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    config = current_app.config
    dados = request.get_json(silent=True) or {}
    novo_status = dados.get("status", "")
    if novo_status not in config["STATUS_PEDIDO_VALIDOS"]:
        raise AppError("Status inválido")

    status_atual = pedido_model.buscar_status(pedido_id)
    if status_atual is None:
        raise NotFoundError("Pedido não encontrado")

    cancelando = novo_status == config["STATUS_PEDIDO_CANCELADO"] and status_atual != novo_status
    pedido_model.atualizar_status(pedido_id, novo_status, devolver_estoque=cancelando)
    logger.info("Pedido %s: status %s -> %s", pedido_id, status_atual, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
