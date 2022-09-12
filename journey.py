from typing import List
from flask import request, redirect, Blueprint
from flask_login import login_required, current_user

from db_model import Puzzle, TeamSolved, TeamArrived, ArrivalCode, SolutionCode, db
from helpers import render, get_current_puzzlehunt

journey = Blueprint('journey', __name__, template_folder='templates', static_folder='static')


@journey.route('/')
@login_required
def index():
    if current_user.is_admin:
        return redirect("/puzzlehunts")  # TODO: different page?

    solved_puzzles = Puzzle.query\
        .filter_by(id_puzzlehunt=get_current_puzzlehunt())\
        .join(TeamSolved)\
        .all()
    open_puzzles = Puzzle.query\
        .filter_by(id_puzzlehunt=get_current_puzzlehunt())\
        .join(TeamArrived)\
        .filter(Puzzle.id_puzzle.not_in(
            TeamSolved.query
            .filter_by(id_team=current_user.id_team)
            .with_entities(TeamSolved.id_puzzle))
        ).all()
    return render("index.html", solved_puzzles=solved_puzzles, open_puzzles=open_puzzles)


@journey.route("/submit", methods=("POST",))
@login_required
def submit_code():
    code = request.form["code"]

    # check solutions for open puzzles
    # TODO: remove already solved
    open_puzzles_ids_query = TeamArrived.query\
        .filter_by(id_team=current_user.id_team)\
        .with_entities(TeamArrived.id_puzzle)
    open_puzzles_solution_codes: List[SolutionCode] = SolutionCode.query\
        .filter(SolutionCode.id_puzzle.in_(open_puzzles_ids_query))\
        .all()
    for solution in open_puzzles_solution_codes:
        if solution.code == code:
            # TODO: repeated code
            team_solved = TeamSolved(current_user.id_team, solution.id_puzzle)
            db.session.add(team_solved)
            db.session.commit()
            # TODO: flash message

    # check arrival codes for not open puzzles
    # TODO: restrict by prerequisites
    not_open_puzzles_ids_query = Puzzle.query\
        .filter_by(id_puzzlehunt=get_current_puzzlehunt())\
        .filter(Puzzle.id_puzzle.not_in(open_puzzles_ids_query))\
        .with_entities(Puzzle.id_puzzle)
    not_open_puzzles_codes: List[ArrivalCode] = ArrivalCode.query\
        .filter(ArrivalCode.id_puzzle.in_(not_open_puzzles_ids_query))\
        .all()
    for arrival in not_open_puzzles_codes:
        if arrival.code == code:
            # TODO: repeated code
            team_arrived = TeamArrived(current_user.id_team, arrival.id_puzzle)
            db.session.add(team_arrived)
            db.session.commit()
            # TODO: flash message

    # TODO: check puzzlehunt global codes

    return redirect("/")
