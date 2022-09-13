from datetime import datetime
from flask import redirect, Blueprint, request, flash
from flask_login import login_required, current_user

from db_model import Puzzle, TeamSolved, TeamArrived, db, Team, TeamSubmittedCode, Code, TeamUsedHint, Hint
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
    team_submitted_codes = TeamSubmittedCode.query \
        .filter_by(id_team=id_team) \
        .join(Code) \
        .all()
    team_used_hints = TeamUsedHint.query \
        .filter_by(id_team=id_team) \
        .join(Hint) \
        .all()

    history = team_solves + team_arrivals + team_submitted_codes + team_used_hints
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


@history_blueprint.route('/history/<id_team>/arrival/<id_puzzle>/delete', methods=("POST",))
@admin_required
def arrival_delete(id_team, id_puzzle):
    arrival = TeamArrived.query.get((id_team, id_puzzle))
    if arrival is None:
        flash(f'Příchod neexistuje.', "danger")
    else:
        team = arrival.team
        puzzle = arrival.puzzle
        db.session.delete(arrival)
        db.session.commit()
        flash(f'Příchod týmu "{team.name}" na šifru "{puzzle.puzzle}" smazán.', "success")
    return redirect(f"/history/{id_team}")


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


@history_blueprint.route('/history/<id_team>/solve/<id_puzzle>/delete', methods=("POST",))
@admin_required
def solve_delete(id_team, id_puzzle):
    solve = TeamSolved.query.get((id_team, id_puzzle))
    if solve is None:
        flash(f'Vyřešení neexistuje.', "danger")
    else:
        team = solve.team
        puzzle = solve.puzzle
        db.session.delete(solve)
        db.session.commit()
        flash(f'Vyřešení šifry "{puzzle.puzzle}" týmem "{team.name}" smazáno.', "success")
    return redirect(f"/history/{id_team}")


@history_blueprint.route('/history/<id_team>/code/<id_code>', methods=("GET", "POST"))
@admin_required
def code_submit_edit(id_team, id_code):
    code_submit = TeamSubmittedCode.query.get((id_team, id_code))

    if request.method == "POST":
        code_submit.timestamp = datetime.strptime(request.form['timestamp'], '%d.%m.%Y %H:%M:%S')
        db.session.add(code_submit)
        db.session.commit()
        return redirect(f"/history/{id_team}")
    else:
        return render("history_entry_edit.html", heading="Upravit čas zadání kódu", back_url=f"/history/{id_team}", entry=code_submit)


@history_blueprint.route('/history/<id_team>/code/<id_code>/delete', methods=("POST",))
@admin_required
def code_submit_delete(id_team, id_code):
    code_submit = TeamSubmittedCode.query.get((id_team, id_code))
    if code_submit is None:
        flash(f'Zadání kódu neexistuje.', "danger")
    else:
        team = code_submit.team
        code = code_submit.code
        db.session.delete(code_submit)
        db.session.commit()
    flash(f'Zadání kódu "{code.code}" týmem "{team.name}" smazáno.', "success")
    return redirect(f"/history/{id_team}")


@history_blueprint.route('/history/<id_team>/hint/<id_hint>', methods=("GET", "POST"))
@admin_required
def hint_used_edit(id_team, id_hint):
    hint_used = TeamUsedHint.query.get((id_team, id_hint))

    if request.method == "POST":
        hint_used.timestamp = datetime.strptime(request.form['timestamp'], '%d.%m.%Y %H:%M:%S')
        db.session.add(hint_used)
        db.session.commit()
        return redirect(f"/history/{id_team}")
    else:
        return render("history_entry_edit.html", heading="Upravit čas použití nápovědy", back_url=f"/history/{id_team}", entry=hint_used)


@history_blueprint.route('/history/<id_team>/hint/<id_code>/delete', methods=("POST",))
@admin_required
def hint_used_delete(id_team, id_hint):
    hint_used = TeamUsedHint.query.get((id_team, id_hint))
    if hint_used is None:
        flash(f'Použití nápovědy neexistuje.', "danger")
    else:
        team = hint_used.team
        hint = hint_used.hint
        db.session.delete(hint_used)
        db.session.commit()
    flash(f'Použití {hint.order}.nápovědy týmem "{team.name}" smazáno.', "success")
    return redirect(f"/history/{id_team}")

