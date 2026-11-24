from flask import current_app

from src.middlewares.error_handler import AppError


def _eh_numero(valor):
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def validar_produto(dados):
    if not dados:
        raise AppError("Dados inválidos")
    if "nome" not in dados:
        raise AppError("Nome é obrigatório")
    if "preco" not in dados:
        raise AppError("Preço é obrigatório")
    if "estoque" not in dados:
        raise AppError("Estoque é obrigatório")

    config = current_app.config
    nome = dados["nome"]
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", config["CATEGORIA_PADRAO"])

    if not isinstance(nome, str):
        raise AppError("Nome deve ser texto")
    if not _eh_numero(preco):
        raise AppError("Preço deve ser numérico")
    if not _eh_numero(estoque):
        raise AppError("Estoque deve ser numérico")
    if preco < 0:
        raise AppError("Preço não pode ser negativo")
    if estoque < 0:
        raise AppError("Estoque não pode ser negativo")
    if len(nome) < config["NOME_PRODUTO_MIN"]:
        raise AppError("Nome muito curto")
    if len(nome) > config["NOME_PRODUTO_MAX"]:
        raise AppError("Nome muito longo")
    if categoria not in config["CATEGORIAS_VALIDAS"]:
        raise AppError("Categoria inválida. Válidas: " + str(config["CATEGORIAS_VALIDAS"]))

    return {
        "nome": nome,
        "descricao": dados.get("descricao", ""),
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validar_itens_pedido(itens):
    for item in itens:
        if not isinstance(item, dict):
            raise AppError("Item do pedido inválido")
        produto_id = item.get("produto_id")
        quantidade = item.get("quantidade")
        if not isinstance(produto_id, int) or isinstance(produto_id, bool):
            raise AppError("produto_id do item é obrigatório")
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            raise AppError("Quantidade deve ser um inteiro maior que zero")
