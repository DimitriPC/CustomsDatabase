from HelloFlask import app, db
from flask import Flask, render_template, url_for, redirect, request, session
from flask_bcrypt import bcrypt
import sqlite3, json, os
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from datetime import datetime, timedelta
from .models import User, Match, MatchParticipant, MatchTeam, GameParticipantStats, Game
from sqlalchemy import select, insert, func, Integer
from sqlalchemy.orm import joinedload
from random import randint, choice
from flask_login import login_user, login_required, logout_user, current_user
import sys

app.secret_key = "allo"

@app.route('/', methods=["POST", "GET"])
@app.route('/#', methods=["POST", "GET"])
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        enteredPassword = request.form["password"].encode("utf-8")

        stmt = select(User).where(User.username == username)
        user = db.session.scalars(stmt).first()

        # account does not exist
        if not user:
            return render_template(
                "failedLogin.html",
                message="Ce compte n'existe pas. Le username ou le mot de passe pourrait etre errone"
            )

        # account exists but no password
        if not user.password:
            return render_template(
                "failedLogin.html",
                message="Aucun mot de passe configure pour ce compte. Veuillez creer un compte"
            )

        # check password
        if bcrypt.checkpw(enteredPassword, user.password.encode("utf-8")):
            login_user(user)
            if (user.username == "Dimipc"):
                user.is_admin = True;
                session["is_admin"] = user.is_admin
            next = request.args.get("next")
            return redirect(next or url_for('prediction'))

        return render_template(
            "failedLogin.html",
            message="Le mot de passe est incorrect pour ce compte"
        )

    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        user = User.query.filter_by(real_name=username).first()

        # If user already exists
        if user:

            # If password already configured
            if user.password:
                return render_template(
                    "failedRegister.html",
                    message="Ce compte existe deja. Veuillez vous connecter"
                )

            # User exists but no password yet
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password, salt)

            user.password = hashed
            db.session.commit()

            login_user(user)
            return redirect(url_for("prediction"))

        # User does not exist → create new one
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password, salt).decode("utf-8")

        new_user = User(
            real_name=username,
            password=hashed
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("prediction"))

    return render_template("register.html")

@app.route("/logout", methods=["POST"])
def logout():
    logout_user()
    return "logged out"

@app.route('/matches', methods=['GET', 'POST'])
@login_required
def matches():
    return "matches"
        
@app.route('/matches/<int:matchId>', methods=['GET', 'POST'])
@login_required
def match(matchId):
        return "match"

@app.route('/ranking', methods=['GET', 'POST'])
def ranking():
    return "ranking"

#admin route
@app.route('/modification/<int:matchId>', methods=['GET', 'POST'])
@login_required
def modification(matchId):
        return "modification"

#admin route
@app.route('/addGame', methods=['GET', 'POST'])
@login_required
def addGame():
        return "addGame"

