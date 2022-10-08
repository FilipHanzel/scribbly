from __future__ import annotations

import os
import shutil
from typing import Optional

import eventlet
from dotenv import load_dotenv
from eventlet import wsgi
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_session import Session

from app.models import db, register_db_utils
from app.routes import auth, home, project

__all__: list[str] = []


PARENT_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(PARENT_DIR)


def get_flag(name: str) -> bool:
    return os.environ.get(name) in ("True", "true", "1")


def get_env(name: str) -> Optional[str | int]:
    env = os.environ.get(name)
    if env is None:
        return None
    if env.isdigit():
        return int(env)
    return env


def setup_session(app: Flask) -> None:
    """Server side sessions setup."""
    session_path = os.path.join(app.instance_path, "sessions")
    app.config["SESSION_FILE_DIR"] = session_path
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True

    Session(app)

    if get_flag("CLEAN_SESSION") and os.path.exists(session_path):
        shutil.rmtree(session_path)
        os.makedirs(session_path)


def setup_database(app: Flask) -> None:
    """Database connection setup."""
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.instance_path}/app.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = app.debug

    if app.debug:
        register_db_utils(app)

    db.init_app(app)

    migrate = Migrate()
    migrate.init_app(app, db)


def setup_auth(app: Flask) -> None:
    """User authentication and authorization setup."""
    login_manager = LoginManager()
    login_manager.init_app(app)
    auth.register_login_manager(login_manager)

    app.register_blueprint(auth.bp)


def setup_blueprints(app: Flask) -> None:
    """Register all remaining blueprints."""
    app.register_blueprint(home.bp)
    app.register_blueprint(project.bp)


def create_app() -> Flask:
    """Flask application factory function."""
    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder="./templates",
        static_folder="./static",
    )

    app.config["SECRET_KEY"] = get_env("SECRET_KEY")

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    setup_session(app)
    setup_database(app)
    setup_auth(app)
    setup_blueprints(app)

    @app.cli.command("run-eventlet")
    def run_eventlet() -> None:
        """Application startup definition."""
        address = get_env("ADDRESS")
        port = get_env("PORT")

        if app.debug:
            print("[INFO] Starting eventlet in debug mode...")
            from werkzeug._reloader import run_with_reloader

            def run_server() -> None:
                eventlet_socket = eventlet.listen((address, port))
                wsgi.server(eventlet_socket, app, debug=True)

            run_with_reloader(run_server)
        else:
            print("[INFO] Starting eventlet...")
            eventlet_socket = eventlet.listen((address, port))
            wsgi.server(eventlet_socket, app, debug=False)

    return app
