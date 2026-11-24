from src.database.connection import get_db

TABELAS = ("itens_pedido", "pedidos", "produtos", "usuarios")


def apagar_todos_os_dados():
    db = get_db()
    for tabela in TABELAS:
        db.execute(f"DELETE FROM {tabela}")
    db.commit()


def contagens():
    db = get_db()
    db.execute("SELECT 1")
    return {
        tabela: db.execute(f"SELECT COUNT(*) FROM {tabela}").fetchone()[0]
        for tabela in ("produtos", "usuarios", "pedidos")
    }
