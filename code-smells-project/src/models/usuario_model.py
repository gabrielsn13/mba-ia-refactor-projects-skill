from src.database.connection import get_db

CAMPOS_PUBLICOS = "id, nome, email, tipo, criado_em"


def listar():
    rows = get_db().execute(f"SELECT {CAMPOS_PUBLICOS} FROM usuarios").fetchall()
    return [dict(row) for row in rows]


def buscar_por_id(usuario_id):
    row = get_db().execute(
        f"SELECT {CAMPOS_PUBLICOS} FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return dict(row) if row else None


def buscar_com_senha_por_email(email):
    row = get_db().execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def criar(nome, email, senha_hash, tipo="cliente"):
    db = get_db()
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid
