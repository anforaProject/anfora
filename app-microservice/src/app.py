import os
from flask import Flask
from src.models import db
from src.oauth2 import config_oauth
from src.routes import bp


def create_app(config=None):

    app = Flask(__name__)

    # load default config

    app.config.from_object("src.settings")

    # load environment configuratopon

    if "FLASK_CONF" in os.environ:
        app.config.from_envvar("FLASK_CONF")

    if config is not None:

        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith(".py"):
            app.config.from_pyfile(config)

    setup_app(app)
    return app


def setup_app(app):
    @app.before_first_request
    def create_tables():
        db.create_all()

    db.init_app(app)
    config_oauth(app)
    app.register_blueprint(bp, url_prefix="")
