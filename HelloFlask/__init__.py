from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

import os

db = SQLAlchemy()   # create db object (no app yet)
login_manager = LoginManager()

app = Flask(__name__)
app.secret_key = "allo"
CORS(app, origins='*')

app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get("DATABASE_URL") or
    "postgresql://dimitri:4939@localhost:5432/mydb"
)   #change ?
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)    # attach db to app
login_manager.init_app(app)
login_manager.login_view = "login"

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
