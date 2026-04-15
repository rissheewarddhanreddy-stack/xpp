import os
from pathlib import Path

from flask import Flask

from .models import db
from .routes import main_bp
from .services.seed import ensure_demo_data


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    database_url = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(app.instance_path) / 'smart_expense.db'}",
    )

    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret-key"),
        SQLALCHEMY_DATABASE_URI=database_url,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        ensure_demo_data()

    return app
