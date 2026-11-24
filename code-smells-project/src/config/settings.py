import os
import secrets


def _env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes")


class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DEBUG = _env_bool("FLASK_DEBUG", False)
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    ENVIRONMENT = os.environ.get("APP_ENV", "development")
    APP_VERSION = "1.0.0"

    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
    SEED_DEMO_DATA = _env_bool("SEED_DEMO_DATA", True)
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

    CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
    CATEGORIA_PADRAO = "geral"
    STATUS_PEDIDO_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]
    STATUS_PEDIDO_INICIAL = "pendente"
    STATUS_PEDIDO_CANCELADO = "cancelado"
    NOME_PRODUTO_MIN = 2
    NOME_PRODUTO_MAX = 200

    # (faturamento mínimo exclusivo, percentual de desconto), da maior faixa para a menor
    FAIXAS_DESCONTO = [(10000, 0.10), (5000, 0.05), (1000, 0.02)]
