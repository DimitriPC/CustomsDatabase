import os, trueskill, itertools, math
from flask import Blueprint
from HelloFlask.models import *
from flask_login import  login_required, current_user
from flask import url_for, redirect, request, jsonify, send_from_directory
from itertools import combinations
from HelloFlask import app, db

api_bp = Blueprint('api', __name__)

@api_bp.route('/api/users', methods=['GET'])
def users():
    users = User.query.all()
    return jsonify([u.to_json() for u in users])

@api_bp.route('/api/maketeams', methods=['POST'])
def make_teams():
    data = request.get_json()
    usernames = data.get('players', [])
    
    users = User.query.filter(User.username.in_(usernames)).all()
    players = [{'username': u.username, 'rating': trueskill.Rating(mu=u.mu, sigma=u.sigma)} for u in users]

    best_split = find_balanced_teams(players)

    return jsonify({
        'teamA': [p['username'] for p in best_split['team1']],
        'teamB': [p['username'] for p in best_split['team2']],
        'quality': round(best_split['probability'] * 100, 1)
    })

@api_bp.route('/api/winchance', methods=['POST'])
def win_chance():
    data = request.get_json()
    teamA_data = data["teamA"]
    teamB_data = data["teamB"]

    teamA = [{'username': p["username"], 'rating': trueskill.Rating(mu=p["mu"], sigma=p["sigma"])} for p in teamA_data]
    teamB = [{'username': p["username"], 'rating': trueskill.Rating(mu=p["mu"], sigma=p["sigma"])} for p in teamB_data]

    win_prob = win_probability(teamA, teamB)
    return jsonify({'quality': win_prob})
    

@api_bp.route('/quick-teams')
@login_required
def quick_teams():
    return send_from_directory(os.path.join(app.root_path, '..', 'static', 'dist'), 'index.html')
    
@api_bp.route('/assets/<path:filename>')
def react_assets(filename):
    return send_from_directory(os.path.join(app.root_path, '..', 'static', 'dist', 'assets'), filename)


def find_balanced_teams(players):   #players are tuples (username, Rating obj)
    n = len(players)
    half = n // 2
    best_split = None
    best_diff = float('inf')

    for team1 in combinations(players, half):
        team1_usernames = {p['username'] for p in team1}
        team2 = [p for p in players if p['username'] not in team1_usernames]

        prob = win_probability(team1, team2)
        diff = abs(prob - 0.5)

        if diff < best_diff:
            best_diff = diff
            best_split = {
                "team1": list(team1),
                "team2": team2,
                "probability": prob
            }

    return best_split

def win_probability(team1, team2):
    delta_mu = sum(p['rating'].mu for p in team1) - sum(p['rating'].mu for p in team2)
    sum_sigma = sum(p['rating'].sigma ** 2 for p in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (trueskill.BETA * trueskill.BETA) + sum_sigma)
    ts = trueskill.global_env()
    print(f"delta_mu: {delta_mu}")
    print(f"sum_sigma: {sum_sigma}")
    print(f"BETA: {trueskill.BETA}")
    print(f"denom: {denom}")
    print(f"ratio: {delta_mu / denom}")
    print(f"prob: {ts.cdf(delta_mu / denom)}")
    return ts.cdf(delta_mu / denom)