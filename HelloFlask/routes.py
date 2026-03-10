import sqlite3, json, os, itertools, math, sys, trueskill
from flask_login.utils import _get_user
from HelloFlask import app, db
from flask import Flask, render_template, url_for, redirect, request, session, flash, jsonify
from flask_bcrypt import bcrypt
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path
from datetime import datetime, timedelta
from .models import User, Match, MatchParticipant, MatchTeam, GameParticipantStats, Game
from sqlalchemy import select, insert, func, Integer, true
from sqlalchemy.orm import joinedload
from random import randint, choice
from flask_login import login_user, login_required, logout_user, current_user
from trueskill import Rating, TrueSkill
from .models import TeamSide
from werkzeug.utils import secure_filename
from zoneinfo import ZoneInfo
from itertools import combinations




app.secret_key = "allo"

@app.route('/', methods=["POST", "GET"])
@app.route('/#', methods=["POST", "GET"])
@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        enteredPassword = request.form["password"].encode("utf-8")

        stmt = select(User).where(User.real_name == name)
        user = db.session.scalars(stmt).first()

        # account does not exist
        if not user:
            flash("Ce compte n'existe pas. Le username ou le mot de passe pourrait etre errone")
            return redirect(url_for('login'))

        # account exists but no password
        if not user.password:
            flash("Aucun mot de passe configure pour ce compte. Veuillez creer un compte")
            return redirect(url_for('login'))

        # check password
        if bcrypt.checkpw(enteredPassword, user.password.encode("utf-8")):
            login_user(user)
            if (user.real_name == "Dimi"):
                user.is_admin = True;
                session["is_admin"] = user.is_admin
            next = request.args.get("next")
            return redirect(next or url_for('matches'))

        flash("Le mot de passe est incorrect pour ce compte")
        return redirect(url_for('login'))

    return render_template("login.html")

@app.route('/register', methods=['GET', 'POST'])
def register():

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
                return redirect(url_for('login'))

            # User exists but no password yet
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password, salt)

            user.password = hashed
            user.real_name = real_name
            db.session.commit()

            login_user(user)
            return redirect(url_for("add_match"))

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
        return redirect(url_for("matches"))

    return render_template("register.html")

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/matches', methods=['GET', 'POST'])
@login_required
def matches():
    stmt = select(Match);
    matches = db.session.scalars(stmt).all()
    return render_template("matches.html", matches=matches)
        
@app.route('/matches/<int:matchId>', methods=['GET', 'POST'])
@login_required
def games(matchId):
    match = db.session.get(Match, matchId)
    return render_template("game.html", match=match)



#admin route
@app.route('/modification/<int:matchId>', methods=['GET', 'POST'])
@login_required
def modification(matchId):
        return "modification"

#admin route
@app.route('/addGame/<int:matchId>', methods=['GET', 'POST'])
@login_required
def addGame(matchId):
    match = db.session.get(Match, matchId)

    if request.method == 'POST':

        winner_side = request.form.get('winner') 
        home_team_id = request.form.get('home_team_id')
        away_team_id = request.form.get('away_team_id')
        winner_team_id = home_team_id if (winner_side == "home") else away_team_id

        photo = request.files.get('photo')

        if photo and photo.filename:
            filename = secure_filename(photo.filename)
    
            match_folder = os.path.join('HelloFlask/static/uploads', str(match.match_id))
            os.makedirs(match_folder, exist_ok=True)

            save_path = os.path.join('HelloFlask/static/uploads', str(match.match_id), filename)
            photo.save(save_path)

            # store only "2/1234.jpg" in db
            db_path = os.path.join(str(match.match_id), filename)
        
        

        new_game = Game(
            first_to = request.form.get('first_to'),
            r6_map = request.form.get('r6map'),
            match_id = matchId,
            home_team_id = home_team_id,
            away_team_id = away_team_id,
            score_home_team = int(request.form.get('score1')),
            score_away_team = request.form.get('score2'),
            photo_url = db_path,
            winner_team_id = winner_team_id
        )

        winner_team = db.session.get(MatchTeam, winner_team_id)
        winner_team.score += 1;

        db.session.add(new_game)
        db.session.commit()
        db.session.refresh(new_game)

        team_home_ids = [p.user_id for p in new_game.home_team.participants]
        team_away_ids = [p.user_id for p in new_game.away_team.participants]
        record_game(team_home_ids, team_away_ids, winner_team_id)

        return redirect(url_for('addGame', matchId=match.match_id))
    
    return render_template("addGame.html", match=match)

@app.route('/add-match', methods=['GET', 'POST'])
def add_match():
    if request.method == 'POST':
        # 1. Create the match
        new_match = Match(
            creator = current_user.user_id,
            date_match = request.form.get('date_match'),
            status     = request.form.get('status'),
            first_to   = request.form.get('first_to'),
        )
        db.session.add(new_match)
        db.session.flush()  # get new_match.match_id before committing

        # 2. Create the two teams linked to this match
        team1 = MatchTeam(match_id=new_match.match_id, side=TeamSide.HOME)
        team2 = MatchTeam(match_id=new_match.match_id, side=TeamSide.AWAY)
        db.session.add_all([team1, team2])
        db.session.flush()  # get team IDs

        # 3. Create participants for each team
        for i in range(1, 6):
            player_id = request.form.get(f'team1_player_{i}')
            if player_id:
                db.session.add(MatchParticipant(
                    match_team_id=team1.match_team_id,
                    user_id=int(player_id)
                ))

        for i in range(1, 6):
            player_id = request.form.get(f'team2_player_{i}')
            if player_id:
                db.session.add(MatchParticipant(
                    match_team_id=team2.match_team_id,
                    user_id=int(player_id)
                ))

        db.session.commit()
        return redirect(url_for('add_match'))  # or wherever

    # GET — only players needed
    players = User.query.order_by(User.username).all()
    today   = datetime.now().date()
    return render_template('addMatch2.html', players=players, today=today)

@app.route('/enterStats/<int:gameId>', methods=['GET', 'POST'])
def enter_stats(gameId):
    game = db.session.get(Game, gameId)

    if request.method == 'POST':
        for i, participant in enumerate(game.home_team.participants, start=1):
            kills    = request.form.get(f'home_{i}_kills')
            assists  = request.form.get(f'home_{i}_assists')
            deaths   = request.form.get(f'home_{i}_deaths')
            score    = request.form.get(f'home_{i}_score')
            position = request.form.get(f'home_{i}_position')

            # check if stat already exists
            stat = GameParticipantStats.query.filter_by(
                match_participant_id=participant.match_participant_id,
                game_id=gameId
            ).first()

            if stat:
                # update existing
                stat.kills    = int(kills)   if kills    else None
                stat.assists  = int(assists) if assists  else None
                stat.deaths   = int(deaths)  if deaths   else None
                stat.score    = int(score)   if score    else None
                stat.position = position     if position else None
            else:
                # create new
                db.session.add(GameParticipantStats(
                    match_participant_id = participant.match_participant_id,
                    game_id  = gameId,
                    kills    = int(kills)   if kills    else None,
                    assists  = int(assists) if assists  else None,
                    deaths   = int(deaths)  if deaths   else None,
                    score    = int(score)   if score    else None,
                    position = position     if position else None,
                ))

        # Away team participants
        for i, participant in enumerate(game.away_team.participants, start=1):
            kills    = request.form.get(f'away_{i}_kills')
            assists  = request.form.get(f'away_{i}_assists')
            deaths   = request.form.get(f'away_{i}_deaths')
            score    = request.form.get(f'away_{i}_score')
            position = request.form.get(f'away_{i}_position')

            # check if stat already exists
            stat = GameParticipantStats.query.filter_by(
                match_participant_id=participant.match_participant_id,
                game_id=gameId
            ).first()

            if stat:
                # update existing
                stat.kills    = int(kills)   if kills    else None
                stat.assists  = int(assists) if assists  else None
                stat.deaths   = int(deaths)  if deaths   else None
                stat.score    = int(score)   if score    else None
                stat.position = position     if position else None
            else:
                # create new
                db.session.add(GameParticipantStats(
                    match_participant_id = participant.match_participant_id,
                    game_id  = gameId,
                    kills    = int(kills)   if kills    else None,
                    assists  = int(assists) if assists  else None,
                    deaths   = int(deaths)  if deaths   else None,
                    score    = int(score)   if score    else None,
                    position = position     if position else None,
                ))

        db.session.commit()
        return redirect(url_for('games', matchId=game.match_id))
        
    return render_template('gameStats.html', game=game)

@app.route('/ranking', methods=['GET', 'POST'])
def ranking():
    users = db.session.execute(db.select(User)).scalars().all()

    ranking = sorted(
        [(user, 100 * (user.mu - 3 * user.sigma)) for user in users],   #100 factor added for clarity for users
        key=lambda x: x[1],
        reverse=True
    )
    return render_template("ranking.html", ranking=ranking, now=datetime.now(ZoneInfo('America/Montreal')))




def record_game(team_home_ids, team_away_ids, winner):
    env = TrueSkill(draw_probability=0)

    # winner = "away" or "home"
    team1 = User.query.filter(User.user_id.in_(team_home_ids)).all()
    team2 = User.query.filter(User.user_id.in_(team_away_ids)).all()

    t1_ratings = [env.create_rating(u.mu, u.sigma) for u in team1]
    t2_ratings = [env.create_rating(u.mu, u.sigma) for u in team2]

    ranks = [0, 1] if winner == "home" else [1, 0]
    (new_t1, new_t2) = env.rate([t1_ratings, t2_ratings], ranks=ranks)

    for user, new_rating in zip(team1, new_t1):
        user.mu = new_rating.mu
        user.sigma = new_rating.sigma
        user.games = (user.games or 0) + 1

    for user, new_rating in zip(team2, new_t2):
        user.mu = new_rating.mu
        user.sigma = new_rating.sigma
        user.games = (user.games or 0) + 1

    db.session.commit()

@app.route('/match/<int:match_id>/edit', methods=['GET', 'POST'])
def edit_match(match_id):
    return "success"



@app.route('/match/<int:match_id>/complete', methods=['POST'])
def complete_match(match_id):
    match = db.session.get(Match, match_id)
    match.status = 'completed'
    db.session.commit()
    return redirect(url_for('games', matchId=match_id))

@app.route('/api/users', methods=['GET'])
def users():
    return jsonify(
        {
            "users": [
                'arpan',
                'zach',
                'jessie'
            ]
        }
    )


def find_balanced_teams(players):
    n = len(players)
    half = n // 2
    best_split = None
    best_diff = float('inf')
    
    for team1 in combinations(players, half):
        team2 = [p for p in players if p not in team1]
        
        prob = win_probability(team1, team2)  # your formula
        diff = abs(prob - 0.5)
        
        if diff < best_diff:
            best_diff = diff
            best_split = (team1, team2)
    
    return best_split

def win_probability(team1, team2):
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (trueskill.BETA * trueskill.BETA) + sum_sigma)
    ts = trueskill.global_env()
    return ts.cdf(delta_mu / denom)
