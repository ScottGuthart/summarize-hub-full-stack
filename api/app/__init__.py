# import os
from config import Config
from flask import Flask
import logging
from logging.handlers import RotatingFileHandler
import os
from flask_marshmallow import Marshmallow
from apifairy import APIFairy
from redis import Redis
import rq
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
apifairy = APIFairy()


def create_app(config_class=Config):
    app = Flask(__name__, static_folder="../../dist", static_url_path="/")
    app.config.from_object(config_class)

    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.task_queue = rq.Queue("flaskapp-tasks", connection=app.redis)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    apifairy.init_app(app)

    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.api import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    if not app.debug:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/flaskapp.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in"
                " %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Flaskapp startup")

    return app