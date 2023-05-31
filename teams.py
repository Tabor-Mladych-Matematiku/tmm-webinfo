from flask import request, redirect, flash, Blueprint

from db_model import Team, db, Puzzlehunt
from helpers import render, admin_required

teams = Blueprint('teams', __name__, template_folder='templates', static_folder='static')


@teams.route('/teams')
@admin_required
def teams_list():
    teams = Team.query.filter_by(id_puzzlehunt=Puzzlehunt.get_current_id()).order_by(Team.name).all()
    return render("teams.html", teams=teams)


@teams.route('/teams/new', methods=("GET", "POST"))
@admin_required
def teams_new():
    if request.method == "POST":
        team = Team(Puzzlehunt.get_current_id(), request.form["name"], request.form["password"], request.form["phone"], request.form["note"])
        db.session.add(team)
        db.session.commit()
        return redirect("/teams")
    return render("team_edit.html")


@teams.route('/teams/<id_team>', methods=("GET", "POST"))
@admin_required
def teams_edit(id_team):
    team = Team.query.get(id_team)
    if team is None:
        flash(f"Tým s id_team={id_team} neexistuje.", "warning")
        return redirect("/teams")

    if request.method == "POST":
        team.name = request.form["name"]
        if request.form["password"]:
            team.set_password(request.form["password"])
        team.phone = request.form["phone"]
        team.note = request.form["note"]
        db.session.add(team)
        db.session.commit()
        return redirect("/teams")
    else:
        return render("team_edit.html", team=team)


@teams.route('/teams/<id_team>/delete', methods=("POST",))
@admin_required
def teams_delete(id_team):
    team = Team.query.get(id_team)
    if team is None:
        flash(f"Tým s id_team={id_team} neexistuje.", "warning")
        return redirect("/teams")

    db.session.delete(team)
    db.session.commit()
    flash(f'Tým "{team.name}" (id={team.id}) smazán.', "success")
    return redirect("/teams")
