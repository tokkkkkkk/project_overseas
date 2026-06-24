import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

from app.routes.auth import bp_auth
from app.routes.docente import bp_docente
from app.routes.studente import bp_studente
from app.routes.ufficio import bp_ufficio
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(Config)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)

    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_docente, url_prefix="/docente")
    app.register_blueprint(bp_studente, url_prefix="/studente")
    app.register_blueprint(bp_ufficio, url_prefix="/ufficio")

    return app

    # Dove rimandare gli utenti non loggati
    # login_manager.login_view = "auth.login"
