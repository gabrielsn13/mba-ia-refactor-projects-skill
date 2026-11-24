from flask import Blueprint

from src.controllers import pedido_controller, produto_controller, sistema_controller, usuario_controller

bp = Blueprint("api", __name__)

bp.add_url_rule("/", "index", sistema_controller.index, methods=["GET"])
bp.add_url_rule("/health", "health_check", sistema_controller.health_check, methods=["GET"])
bp.add_url_rule("/admin/reset-db", "reset_database", sistema_controller.resetar_banco, methods=["POST"])
bp.add_url_rule("/relatorios/vendas", "relatorio_vendas", sistema_controller.relatorio_vendas, methods=["GET"])

bp.add_url_rule("/produtos", "listar_produtos", produto_controller.listar_produtos, methods=["GET"])
bp.add_url_rule("/produtos/busca", "buscar_produtos", produto_controller.buscar_produtos, methods=["GET"])
bp.add_url_rule("/produtos/<int:produto_id>", "buscar_produto", produto_controller.buscar_produto, methods=["GET"])
bp.add_url_rule("/produtos", "criar_produto", produto_controller.criar_produto, methods=["POST"])
bp.add_url_rule("/produtos/<int:produto_id>", "atualizar_produto", produto_controller.atualizar_produto, methods=["PUT"])
bp.add_url_rule("/produtos/<int:produto_id>", "deletar_produto", produto_controller.deletar_produto, methods=["DELETE"])

bp.add_url_rule("/usuarios", "listar_usuarios", usuario_controller.listar_usuarios, methods=["GET"])
bp.add_url_rule("/usuarios/<int:usuario_id>", "buscar_usuario", usuario_controller.buscar_usuario, methods=["GET"])
bp.add_url_rule("/usuarios", "criar_usuario", usuario_controller.criar_usuario, methods=["POST"])
bp.add_url_rule("/login", "login", usuario_controller.login, methods=["POST"])

bp.add_url_rule("/pedidos", "criar_pedido", pedido_controller.criar_pedido, methods=["POST"])
bp.add_url_rule("/pedidos", "listar_todos_pedidos", pedido_controller.listar_todos_pedidos, methods=["GET"])
bp.add_url_rule(
    "/pedidos/usuario/<int:usuario_id>", "listar_pedidos_usuario", pedido_controller.listar_pedidos_usuario, methods=["GET"]
)
bp.add_url_rule(
    "/pedidos/<int:pedido_id>/status", "atualizar_status_pedido", pedido_controller.atualizar_status_pedido, methods=["PUT"]
)
