import logging

from flask import current_app, jsonify, request

from src.middlewares.error_handler import ForbiddenError
from src.models import admin_model, pedido_model

logger = logging.getLogger(__name__)


def _calcular_desconto(faturamento):
    for minimo, percentual in current_app.config["FAIXAS_DESCONTO"]:
        if faturamento > minimo:
            return faturamento * percentual
    return 0


def relatorio_vendas():
    resumo = pedido_model.resumo_vendas()
    faturamento = resumo["faturamento"]
    total_pedidos = resumo["total_pedidos"]
    por_status = resumo["por_status"]
    desconto = _calcular_desconto(faturamento)

    relatorio = {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": por_status.get("pendente", 0),
        "pedidos_aprovados": por_status.get("aprovado", 0),
        "pedidos_cancelados": por_status.get("cancelado", 0),
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
    return jsonify({"dados": relatorio, "sucesso": True}), 200


def health_check():
    config = current_app.config
    try:
        contagens = admin_model.contagens()
    except Exception:
        logger.exception("Falha no health check")
        return jsonify({"status": "erro", "detalhes": "Banco de dados indisponível"}), 500
    return jsonify(
        {
            "status": "ok",
            "database": "connected",
            "counts": contagens,
            "versao": config["APP_VERSION"],
            "ambiente": config["ENVIRONMENT"],
        }
    ), 200


def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": current_app.config["APP_VERSION"],
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


def resetar_banco():
    token = current_app.config["ADMIN_TOKEN"]
    if not token or request.headers.get("X-Admin-Token") != token:
        raise ForbiddenError("Acesso negado")
    admin_model.apagar_todos_os_dados()
    logger.warning("Banco de dados resetado")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
