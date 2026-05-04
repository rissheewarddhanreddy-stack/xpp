from flask import Flask
from .routes import main_bp

def create_app():
    app = Flask(__name__)

    try:
        app.register_blueprint(main_bp)
    except Exception as e:
        print("Blueprint error:", e)

    @app.route("/health")
    def health():
        return "OK"

    return app