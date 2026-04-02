from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import os

db = SQLAlchemy()   # create db object (no app yet)
login_manager = LoginManager()

# ------------------------- 
# Config classes 
# ------------------------- 
class Config: 
 SECRET_KEY = "dev" 
 
 SQLALCHEMY_DATABASE_URI = "postgresql://dimitri:4939@localhost:5432/mydb"
 
 SQLALCHEMY_TRACK_MODIFICATIONS = False 
 
class TestConfig: 
 TESTING = True 
 SECRET_KEY = "test" 

 SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:" 
 
 SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app(config_class=Config):
    app = Flask(__name__)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    app.config.from_object(config_class)

    CORS(app, origins='*')

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .routes.matches import matches_bp
    from .routes.users import users_bp
    from .routes.api import api_bp
    from .routes.admin import admin_bp
    from .routes.auth import auth_bp


    app.register_blueprint(matches_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app




