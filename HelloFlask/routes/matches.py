from flask import Blueprint, render_template
from HelloFlask.models import *
from flask_login import login_required, current_user
from flask import render_template, url_for, redirect, request
from werkzeug.utils import secure_filename
import os

matches_bp = Blueprint('matches', __name__)

@matches_bp.route('/matches', methods=['GET', 'POST'])
@login_required
def matches():
    matches = Match.query.order_by(Match.date_match.desc()).all()
    return render_template("matches.html", matches=matches)
        
@matches_bp.route('/matches/<int:matchId>', methods=['GET', 'POST'])
@login_required
def games(matchId):
    match = db.session.get(Match, matchId)
    return render_template("game.html", match=match)

#admin route
@matches_bp.route('/addGame/<int:matchId>', methods=['GET', 'POST'])
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

        db.session.add(new_game)
        db.session.commit()
        

        return redirect(url_for('matches.addGame', matchId=match.match_id))
    
    return render_template("addGame.html", match=match)

@matches_bp.route('/add-match', methods=['GET', 'POST'])
def add_match():
    if request.method == 'POST':
        # 1. Create the match
        new_match = Match(
            creator = current_user.user_id,
            date_match = request.form.get('date_match'),
            status     = request.form.get('status'),
            first_to   = request.form.get('first_to'),
            description = request.form.get('description') or None
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
        return redirect(url_for('matches.add_match'))  # or wherever

    # GET — only players needed
    players = User.query.order_by(User.username).all()
    today   = datetime.now().date()
    return render_template('addMatch2.html', players=players, today=today)

@matches_bp.route('/enterStats/<int:gameId>', methods=['GET', 'POST'])
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
        return redirect(url_for('matches.games', matchId=game.match_id))
        
    return render_template('gameStats.html', game=game)

@matches_bp.route('/match/<int:match_id>/complete', methods=['POST'])
def complete_match(match_id):
    match = db.session.get(Match, match_id)
    match.status = 'completed'
    db.session.commit()
    return redirect(url_for('matches.games', matchId=match_id))