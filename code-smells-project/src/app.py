import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import Settings
from src.database.connection import init_db
from src.middlewares.error_handler import register_error_handlers
from src.views.routes import bp


def create_app(settings=Settings):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = Flask(__name__)
    app.config.from_object(settings)
    CORS(app)
    init_db(app)
    register_error_handlers(app)
    app.register_blueprint(bp)
    return app
