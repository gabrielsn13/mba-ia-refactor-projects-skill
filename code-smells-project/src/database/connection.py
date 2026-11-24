import sqlite3

from flask import current_app, g

from src.database.schema import SCHEMA
from src.database.seed import seed_demo_data


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    with app.app_context():
        db = get_db()
        for statement in SCHEMA:
            db.execute(statement)
        db.commit()
        if app.config["SEED_DEMO_DATA"]:
            seed_demo_data(db)
        close_db()
    app.teardown_appcontext(close_db)
