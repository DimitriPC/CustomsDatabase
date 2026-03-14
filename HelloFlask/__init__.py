from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
import os


db = SQLAlchemy()   # create db object (no app yet)
login_manager = LoginManager()

app = Flask(__name__)
CORS(app, origins='*')

app.config["SQLALCHEMY_DATABASE_URI"] = (
    os.environ.get("DATABASE_URL") or
    "postgresql://dimitri:4939@localhost:5432/mydb"
)   #change ?
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)    # attach db to app
login_manager.init_app(app)
login_manager.login_view = "login"

from .models import User
from . import models
from . import routes


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
