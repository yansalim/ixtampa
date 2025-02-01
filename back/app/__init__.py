# app/__init__.py
from flask import Flask
from app.config import Config
from app.extensions import db, jwt, swagger

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializa as extensões
    db.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)

    # Registra os blueprints
    from app.routes.upload import upload_bp
    from app.routes.preview import preview_bp
    from app.routes.auth import auth_bp
    from app.routes.subscription import subscription_bp

    app.register_blueprint(upload_bp)
    app.register_blueprint(preview_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(subscription_bp)

    # Cria as tabelas do banco de dados
    with app.app_context():
        db.create_all()

    return app