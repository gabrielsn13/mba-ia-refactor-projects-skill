import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import Settings
from src.database.db import db
from src.middlewares.auth import authenticate
from src.middlewares.error_handler import register_error_handlers
from src.utils.time import utc_now
from src.views import auth_routes, category_routes, report_routes, task_routes, user_routes


def create_app(config=Settings):
    app = Flask(__name__)
    app.config.from_object(config)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')

    CORS(app, origins=app.config['CORS_ORIGINS'])
    db.init_app(app)

    app.before_request(authenticate)
    register_error_handlers(app)

    for module in (auth_routes, task_routes, user_routes, category_routes, report_routes):
        app.register_blueprint(module.bp)

    @app.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(utc_now())}

    @app.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': '1.0'}

    with app.app_context():
        db.create_all()

    return app
