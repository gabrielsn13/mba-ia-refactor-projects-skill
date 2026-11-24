from src.database.connection import get_db


class EstoqueInsuficienteError(Exception):
    def __init__(self, produto_id):
        super().__init__(f"Estoque insuficiente para o produto {produto_id}")
        self.produto_id = produto_id


def criar_com_itens(usuario_id, status, total, itens):
    """Cria pedido, itens e baixa de estoque em uma única transação."""
    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
            (usuario_id, status, total),
        )
        pedido_id = cursor.lastrowid
        for item in itens:
            db.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"]),
            )
            baixa = db.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                (item["quantidade"], item["produto_id"], item["quantidade"]),
            )
            if baixa.rowcount == 0:
                raise EstoqueInsuficienteError(item["produto_id"])
        db.commit()
        return pedido_id
    except Exception:
        db.rollback()
        raise


def _listar_com_itens(where="", params=()):
    rows = get_db().execute(
        f"""
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido i ON i.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = i.produto_id
        {where}
        ORDER BY p.id, i.id
        """,
        params,
    ).fetchall()
    pedidos = {}
    for row in rows:
        pedido = pedidos.setdefault(
            row["id"],
            {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            },
        )
        if row["produto_id"] is not None:
            pedido["itens"].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
    return list(pedidos.values())


def listar_todos():
    return _listar_com_itens()


def listar_por_usuario(usuario_id):
    return _listar_com_itens("WHERE p.usuario_id = ?", (usuario_id,))


def buscar_status(pedido_id):
    row = get_db().execute("SELECT status FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
    return row["status"] if row else None


def atualizar_status(pedido_id, novo_status, devolver_estoque=False):
    db = get_db()
    try:
        db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
        if devolver_estoque:
            db.execute(
                """
                UPDATE produtos
                SET estoque = estoque + (
                    SELECT COALESCE(SUM(quantidade), 0) FROM itens_pedido
                    WHERE pedido_id = ? AND produto_id = produtos.id
                )
                WHERE id IN (SELECT produto_id FROM itens_pedido WHERE pedido_id = ?)
                """,
                (pedido_id, pedido_id),
            )
        db.commit()
    except Exception:
        db.rollback()
        raise


def resumo_vendas():
    db = get_db()
    totais = db.execute("SELECT COUNT(*) AS qtd, SUM(total) AS faturamento FROM pedidos").fetchone()
    por_status = {
        row["status"]: row["qtd"]
        for row in db.execute("SELECT status, COUNT(*) AS qtd FROM pedidos GROUP BY status").fetchall()
    }
    return {
        "total_pedidos": totais["qtd"],
        "faturamento": totais["faturamento"] or 0,
        "por_status": por_status,
    }
