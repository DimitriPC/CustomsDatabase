from flask import Blueprint, render_template
from flask import render_template, url_for, redirect, request, session, flash, abort
from HelloFlask.models import *
from flask_bcrypt import bcrypt
from flask_login import login_user, logout_user



auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=["POST", "GET"])
@auth_bp.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        enteredPassword = request.form["password"].encode("utf-8")

        stmt = select(User).where(User.real_name == name)
        user = db.session.scalars(stmt).first()

        # account does not exist
        if not user:
            flash("Ce compte n'existe pas. Le username ou le mot de passe pourrait etre errone")
            return redirect(url_for('auth.login'))

        # account exists but no password
        if not user.password:
            flash("Aucun mot de passe configure pour ce compte. Veuillez creer un compte")
            return redirect(url_for('auth.login'))

        # check password
        if bcrypt.checkpw(enteredPassword, user.password.encode("utf-8")):
            if (user.username == 'Dimipc'):
                user.is_admin = True
            session["is_admin"] = user.is_admin
            login_user(user)
            next = request.args.get("next")
            return redirect(next or url_for('matches.matches'))

        flash("Le mot de passe est incorrect pour ce compte")
        return redirect(url_for('auth.login'))

    return render_template("login.html")

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    abort(404)
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")
        real_name = request.form["real_name"]

        user = User.query.filter_by(real_name=username).first()

        # If user already exists
        if user:

            # If password already configured
            if user.password:
                flash("Ce compte existe deja. Veuillez vous connecter")
                return redirect(url_for('auth.login'))

            # User exists but no password yet
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password, salt)

            user.password = hashed
            user.real_name = real_name
            db.session.commit()

            login_user(user)
            return redirect(url_for("matches.add_match"))

        # User does not exist → create new one
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt).decode("utf-8")

        new_user = User(
            real_name=real_name,
            password=hashed,
            username=username
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("matches.matches"))

    return render_template("register.html")

@auth_bp.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))