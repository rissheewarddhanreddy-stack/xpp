from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///smart_expense.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config is not None:
        app.config.update(test_config)

    db.init_app(app)

    from .routes import main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app
