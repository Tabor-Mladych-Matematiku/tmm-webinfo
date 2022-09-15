from collections import defaultdict
from typing import List
from flask import Blueprint
from sqlalchemy import func

from db_model import Puzzle, Team, TeamArrived, TeamSolved, TeamUsedHint, Hint, TeamSubmittedCode
from helpers import render, get_current_puzzlehunt, admin_required
from puzzlehunts import get_settings_for_puzzlehunt

progress_table = Blueprint('progress_table', __name__, template_folder='templates', static_folder='static')


@progress_table.route('/progress')
@admin_required
def progress():
    puzzles = Puzzle.query.filter_by(id_puzzlehunt=get_current_puzzlehunt()).order_by(Puzzle.order).all()
    teams = Team.query.filter_by(id_puzzlehunt=get_current_puzzlehunt()).order_by(Team.name).all()
    team_ids = Team.query.filter_by(id_puzzlehunt=get_current_puzzlehunt()).with_entities(Team.id_team)

    arrivals: List[TeamArrived] = TeamArrived.query\
        .filter(TeamArrived.id_team.in_(team_ids)).all()
    solves: List[TeamSolved] = TeamSolved.query\
        .filter(TeamSolved.id_team.in_(team_ids)).all()

    hints_used: List[int] = TeamUsedHint.query\
        .filter(TeamUsedHint.id_team.in_(team_ids))\
        .join(Hint)\
        .with_entities(TeamUsedHint.id_team, Hint.id_puzzle, func.count(Hint.id_hint))\
        .group_by(TeamUsedHint.id_team, Hint.id_puzzle)\
        .all()

    arrival_times = defaultdict(dict)
    for arrival in arrivals:
        arrival_times[arrival.id_team][arrival.id_puzzle] = arrival.timestamp.strftime("%H:%M")

    solve_times = defaultdict(dict)
    for solve in solves:
        solve_times[solve.id_team][solve.id_puzzle] = solve.timestamp.strftime("%H:%M")

    hints = defaultdict(lambda: defaultdict(int))
    for id_team, id_puzzle, hint_count in hints_used:
        hints[id_team][id_puzzle] = hint_count
        hints[id_team]["sum"] += hint_count

    puzzlehunt_settings = get_settings_for_puzzlehunt(get_current_puzzlehunt())
    finish_times = {}
    if "finish_code" in puzzlehunt_settings:
        try:
            finish_code = int(puzzlehunt_settings["finish_code"].value)
            for finish in TeamSubmittedCode.query\
                    .filter_by(id_code=finish_code)\
                    .filter(TeamSubmittedCode.id_team.in_(team_ids)):
                finish_times[finish.id_team] = finish.timestamp.strftime("%H:%M")
        except ValueError:
            pass

    return render("progress_table.html", puzzles=puzzles, teams=teams,
                  arrival_times=arrival_times, solve_times=solve_times, hints=hints, finish_times=finish_times)
