from typing import List
from flask import request, redirect, Blueprint, flash
from flask_login import login_required, current_user

from codes import compare_codes
from db_model import Puzzle, TeamSolved, TeamArrived, ArrivalCode, SolutionCode, db, PuzzlePrerequisite, Code, \
    TeamSubmittedCode, Hint, TeamUsedHint
from helpers import render, get_current_puzzlehunt, admin_required

journey = Blueprint('journey', __name__, template_folder='templates', static_folder='static')


@journey.route('/')
@login_required
def index():
    if current_user.is_admin:
        return redirect("/puzzlehunts")  # TODO: different page?

    team_solves_with_arrivals = TeamSolved.query\
        .filter_by(id_team=current_user.id_team)\
        .join(Puzzle)\
        .join(TeamArrived,
              (TeamSolved.id_puzzle == TeamArrived.id_puzzle) & (TeamSolved.id_team == TeamArrived.id_team))\
        .with_entities(TeamSolved, TeamArrived)\
        .all()
    team_arrivals = TeamArrived.query\
        .filter_by(id_team=current_user.id_team)\
        .join(Puzzle)\
        .filter(Puzzle.id_puzzle.not_in(
            TeamSolved.query
                .filter_by(id_team=current_user.id_team)
                .with_entities(TeamSolved.id_puzzle)))\
        .all()
    team_submitted_codes = TeamSubmittedCode.query \
        .filter_by(id_team=current_user.id_team) \
        .order_by(TeamSubmittedCode.timestamp.desc())\
        .join(Code)\
        .all()

    return render("index.html", solves=team_solves_with_arrivals, arrivals=team_arrivals, submitted_codes=team_submitted_codes)


@journey.route("/submit", methods=("POST",))
@login_required
def submit_code(id_team=None):
    code = request.form["code"]
    if id_team is None:
        id_team = current_user.id_team
    else:
        if not current_user.is_admin:
            flash("Tato operace je dostupná pouze organizátorům.", "danger")
            return redirect("/")

    solved_puzzles_ids_query = TeamSolved.query\
        .filter_by(id_team=id_team)\
        .with_entities(TeamSolved.id_puzzle)
    open_puzzles_ids_query = TeamArrived.query\
        .filter_by(id_team=id_team)\
        .filter(TeamArrived.id_puzzle.not_in(solved_puzzles_ids_query))\
        .with_entities(TeamArrived.id_puzzle)

    # check solutions for open puzzles
    open_puzzles_solution_codes: List[SolutionCode] = SolutionCode.query\
        .filter(SolutionCode.id_puzzle.in_(open_puzzles_ids_query))\
        .all()
    for solution in open_puzzles_solution_codes:
        if compare_codes(code, solution.code):
            team_solved = TeamSolved(id_team, solution.id_puzzle, solution.id_solution_code)
            db.session.add(team_solved)
            db.session.commit()
            flash(f'Řešení "{solution.code}" je správně.', "success")
            return redirect("/")

    # check arrival codes for not open puzzles
    not_open_puzzles_ids_query = Puzzle.query\
        .filter_by(id_puzzlehunt=get_current_puzzlehunt())\
        .filter(Puzzle.id_puzzle.not_in(open_puzzles_ids_query))\
        .filter(Puzzle.id_puzzle.not_in(solved_puzzles_ids_query))\
        .with_entities(Puzzle.id_puzzle)
    not_open_puzzles_codes: List[ArrivalCode] = ArrivalCode.query\
        .filter(ArrivalCode.id_puzzle.in_(not_open_puzzles_ids_query))\
        .all()
    for arrival in not_open_puzzles_codes:
        if compare_codes(code, arrival.code):
            prerequisites = PuzzlePrerequisite.query\
                .filter_by(id_new_puzzle=arrival.id_puzzle)\
                .with_entities(PuzzlePrerequisite.id_previous_puzzle)
            fulfilled_prerequisites = TeamSolved.query\
                .filter_by(id_team=id_team)\
                .filter(TeamSolved.id_puzzle.in_(prerequisites))
            if fulfilled_prerequisites.count() < prerequisites.count():
                flash(f'Nejdřív musíte vyřešit předchozí šifry.', "danger")
                return redirect("/")

            team_arrived = TeamArrived(id_team, arrival.id_puzzle, arrival.id_arrival_code)
            db.session.add(team_arrived)
            db.session.commit()
            flash(f'Kód stanoviště "{arrival.code}" je správný. Šifra "{arrival.puzzle.puzzle}" otevřena.', "success")
            return redirect("/")

    not_used_puzzlehunt_codes = Code.query\
        .filter_by(id_puzzlehunt=get_current_puzzlehunt())\
        .filter(Code.id_code.not_in(
            TeamSubmittedCode.query
                .filter_by(id_team=id_team)
                .with_entities(TeamSubmittedCode.id_code)))\
        .all()
    for puzzlehunt_code in not_used_puzzlehunt_codes:
        if compare_codes(code, puzzlehunt_code.code):
            team_submitted_code = TeamSubmittedCode(id_team, puzzlehunt_code.id_code)
            db.session.add(team_submitted_code)
            db.session.commit()
            flash(f'Kód "{puzzlehunt_code.code}" je správný.', "success")
            return redirect("/")

    flash(f'Kód "{code}" není správný (nebo už byl zadán).', "danger")
    return redirect("/")


@journey.route("/submit/<id_team>", methods=("POST",))
@admin_required
def submit_code_admin(id_team):
    submit_code(id_team)
    return redirect(f"/history/{id_team}")


@journey.route("/hint/<id_hint>", methods=("POST",))
@login_required
def use_hint(id_hint, id_team=None):
    if id_team is None:
        id_team = current_user.id_team
    else:
        if not current_user.is_admin:
            flash("Tato operace je dostupná pouze organizátorům.", "danger")
            return redirect("/")

    hint = Hint.query.get(id_hint)
    if hint is None:
        flash(f"Nápověda neexistuje.", "warning")
        return redirect("/")
    team_arrival = TeamArrived.query.get((id_team, hint.id_puzzle))
    if team_arrival is None:
        flash(f"Nejprve zadejte kód stanoviště.", "warning")
        return redirect("/")
    if not hint.is_open(team_arrival.timestamp):
        flash(f"Nápověda ještě není k dispozici.", "warning")
        return redirect("/")

    team_used_hint = TeamUsedHint(id_team, id_hint)
    db.session.add(team_used_hint)
    db.session.commit()
    flash(f'Nápověda použita.', "success")
    return redirect("/")


@journey.route("/hint_team/<id_team>", methods=("POST",))
@admin_required
def hint_team_admin(id_team):
    id_hint = request.form['id_hint']
    use_hint(id_hint, id_team)
    return redirect(f"/history/{id_team}")
