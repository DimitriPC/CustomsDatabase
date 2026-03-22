from flask import Blueprint, render_template
from flask import render_template, url_for, redirect, request
from HelloFlask.models import *
from flask_login import login_required
from trueskill import TrueSkill, Rating
from zoneinfo import ZoneInfo


users_bp = Blueprint('users', __name__)

@users_bp.route('/ranking', methods=['GET', 'POST'])
def ranking():
    if request.method == 'POST':
        update_all_ratings()
        return redirect(url_for('users.ranking'))
    users = db.session.execute(db.select(User)).scalars().all()

    ranking = sorted(
        [(user, 100 * (user.mu - 3 * user.sigma)) for user in users],   #100 factor added for clarity for users
        key=lambda x: x[1],
        reverse=True
    )
    return render_template("ranking.html", ranking=ranking, now=datetime.now(ZoneInfo('America/Montreal')))

@users_bp.route('/user/<int:user_id>')
@login_required
def user_profile(user_id):
    profile_user = db.session.get(User, user_id)
    # get all matches this user participated in
    matches = Match.query.join(MatchTeam).join(MatchParticipant)\
        .filter(MatchParticipant.user_id == user_id)\
        .order_by(Match.date_match.desc()).all()
    return render_template('user_profile.html', profile_user=profile_user, matches=matches)

@users_bp.route('/user/<int:user_id>/boost-sigma', methods=['POST'])
@login_required
def boost_sigma(user_id):
    if not current_user.is_admin:
        return redirect(url_for('users.user_profile', user_id=user_id))
    user = db.session.get(User, user_id)
    new_sigma = request.form.get('new_sigma')
    if new_sigma:
        user.sigma = float(new_sigma)
        db.session.commit()
    return redirect(url_for('users.user_profile', user_id=user_id))


def update_all_ratings():
    # reset all users first
    users = db.session.execute(db.select(User)).scalars().all()
    for user in users:
        user.mu = 25.0
        user.sigma = 8.333
        user.games = 0
        user.wins = 0
        user.losses = 0

    # build a lookup so we always read the latest in-memory values
    user_map = {user.user_id: user for user in users}

    env = TrueSkill(draw_probability=0)
    games = db.session.execute(
        db.select(Game).where(Game.winner_team_id != None).order_by(Game.game_id)
    ).scalars().all()

    for game in games:
        home_participants = [p for p in game.home_team.participants]
        away_participants = [p for p in game.away_team.participants]
        if not home_participants or not away_participants:
            continue

        # use user_map to get current in-memory mu/sigma
        home_ratings = {
            p.user_id: Rating(mu=user_map[p.user_id].mu, sigma=user_map[p.user_id].sigma)
            for p in home_participants
        }
        away_ratings = {
            p.user_id: Rating(mu=user_map[p.user_id].mu, sigma=user_map[p.user_id].sigma)
            for p in away_participants
        }

        if game.winner_team_id == game.home_team_id:
            ranks = [0, 1]
        else:
            ranks = [1, 0]

        new_home, new_away = env.rate([home_ratings, away_ratings], ranks=ranks)

        for user_id, new_rating in new_home.items():
            u = user_map[user_id]
            u.mu = new_rating.mu
            u.sigma = new_rating.sigma
            u.games += 1
            u.wins += 1 if game.winner_team_id == game.home_team_id else 0
            u.losses += 1 if game.winner_team_id != game.home_team_id else 0

        for user_id, new_rating in new_away.items():
            u = user_map[user_id]
            u.mu = new_rating.mu
            u.sigma = new_rating.sigma
            u.games += 1
            u.wins += 1 if game.winner_team_id == game.away_team_id else 0
            u.losses += 1 if game.winner_team_id != game.away_team_id else 0

    db.session.commit()