import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db, Usuario

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET'],
        secure=True
    )

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.velas import velas_bp
    from app.routes.oraciones import oraciones_bp
    from app.routes.categorias import categorias_bp
    from app.routes.public import public_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(velas_bp)
    app.register_blueprint(oraciones_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(public_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    return app
