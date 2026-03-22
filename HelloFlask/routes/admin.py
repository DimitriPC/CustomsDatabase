from flask import Blueprint, render_template
from flask import render_template, url_for, redirect, request, flash
from HelloFlask.models import *
from flask_login import login_required
from flask_bcrypt import bcrypt


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/match/<int:match_id>/delete', methods=['POST'])
def delete_match(match_id):  
    match = db.session.get(Match, match_id)
    db.session.delete(match)
    db.session.commit()
    return redirect(url_for('matches.matches'))

@admin_bp.route('/game/<int:game_id>/delete', methods=['POST'])
def delete_game(game_id):  
    game = db.session.get(Game, game_id)
    match_id = game.match_id
    db.session.delete(game)
    db.session.commit()
    return redirect(url_for('matches.games', matchId=match_id))

@admin_bp.route('/admin/user/<int:user_id>/change-password', methods=['POST'])
@login_required
def admin_change_password(user_id):
    
    new_pw = request.form['new_password']
    confirm_pw = request.form['confirm_password']
    if new_pw != confirm_pw:
        flash('Passwords do not match.', 'error')
        return redirect(url_for('users.user_profile', user_id=user_id))

    user = User.query.get(user_id)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(new_pw.encode("utf-8"), salt)
    user.password = hashed.decode('utf-8')

    db.session.commit()
    flash('Password updated.', 'success')
    return redirect(url_for('users.user_profile', user_id=user_id))