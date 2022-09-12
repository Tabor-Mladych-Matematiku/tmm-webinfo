from datetime import datetime

from flask import redirect, Blueprint, request
from flask_login import login_required, current_user

from db_model import Puzzle, TeamSolved, TeamArrived, db, Team
from helpers import render, admin_required

history_blueprint = Blueprint('history', __name__, template_folder='templates', static_folder='static')


@history_blueprint.route('/history')
@login_required
def history(id_team=None):
    if id_team is None:
        if current_user.is_admin:
            return redirect("/progress")
        id_team = current_user.id_team
    team = Team.query.get(id_team)

    team_solves = TeamSolved.query\
        .filter_by(id_team=id_team)\
        .join(Puzzle)\
        .all()
    team_arrivals = TeamArrived.query\
        .filter_by(id_team=id_team)\
        .join(Puzzle)\
        .all()

    history = team_solves + team_arrivals
    history = reversed(sorted(history, key=lambda e: e.timestamp))

    return render("history.html", history=history, team=team)


@history_blueprint.route('/history/<id_team>')
@admin_required
def team_history(id_team):
    return history(id_team)


@history_blueprint.route('/history/<id_team>/arrival/<id_puzzle>', methods=("GET", "POST"))
@admin_required
def arrival_edit(id_team, id_puzzle):
    arrival = TeamArrived.query.get((id_team, id_puzzle))

    if request.method == "POST":
        arrival.timestamp = datetime.strptime(request.form['timestamp'], '%d.%m.%Y %H:%M:%S')
        db.session.add(arrival)
        db.session.commit()
        return redirect(f"/history/{id_team}")
    else:
        return render("history_entry_edit.html", heading="Upravit čas příchodu", back_url=f"/history/{id_team}", entry=arrival)


@history_blueprint.route('/history/<id_team>/solve/<id_puzzle>', methods=("GET", "POST"))
@admin_required
def solve_edit(id_team, id_puzzle):
    solve = TeamSolved.query.get((id_team, id_puzzle))

    if request.method == "POST":
        solve.timestamp = datetime.strptime(request.form['timestamp'], '%d.%m.%Y %H:%M:%S')
        db.session.add(solve)
        db.session.commit()
        return redirect(f"/history/{id_team}")
    else:
        return render("history_entry_edit.html", heading="Upravit čas vyřešení", back_url=f"/history/{id_team}", entry=solve)
