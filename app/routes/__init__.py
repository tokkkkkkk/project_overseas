import sqlalchemy as sq
from flask import Flask

app = Flask(__name__)
engine = sq.create_engine(
    "postgresql://postgres:[YOUR-PASSWORD]@db.nhdjencfjpmydjkzgzcd.supabase.co:5432/postgres",
    echo=True,
)

app.secret_key = b'_5#tkL"F4Q8z\n\xec]/'


# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Crea le istanze delle estensioni (ancora non collegate all'app)
db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    # Crea l'applicazione Flask
    app = Flask(__name__)

    # Carica la configurazione
    app.config.from_object(Config)

    # Collega le estensioni all'app
    db.init_app(app)
    login_manager.init_app(app)

    # Dove rimandare gli utenti non loggati
    login_manager.login_view = "auth.login"

    # Registra le route (i "gruppi" di URL)
    from app.routes.auth import auth_bp
    from app.routes.studente import studente_bp
    from app.routes.docente import docente_bp
    from app.routes.ufficio import ufficio_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(studente_bp, url_prefix="/studente")
    app.register_blueprint(docente_bp, url_prefix="/docente")
    app.register_blueprint(ufficio_bp, url_prefix="/ufficio")

    return app

