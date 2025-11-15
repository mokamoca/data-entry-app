from flask import Flask
from flask_wtf import CSRFProtect

from .config import Config
from .database import init_app as init_database, session_cleanup

csrf = CSRFProtect()


def create_app(config_class: type[Config] = Config):
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(config_class)

    if not app.config.get("SECRET_KEY"):
        raise RuntimeError("SECRET_KEY environment variable must be set for this app.")

    # Ensure baseline choices are available even if env vars were empty.
    app.config.setdefault("SHIFT_CHOICES", ["A", "B", "C"])
    app.config.setdefault("MACHINE_CHOICES", [2, 3, 4, 5, 6])
    app.config.setdefault("MODEL_CHOICES", [f"sample{i}" for i in range(1, 11)])

    csrf.init_app(app)
    init_database(app)

    from .routes import bp as main_bp

    app.register_blueprint(main_bp)
    app.teardown_appcontext(session_cleanup)

    return app

