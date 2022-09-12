from collections import defaultdict
from typing import List
from flask import Blueprint

from db_model import Puzzle, Team, TeamArrived, TeamSolved
from helpers import render, get_current_puzzlehunt, admin_required

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
        .filter(TeamArrived.id_team.in_(team_ids)).all()

    arrival_times = defaultdict(dict)
    for arrival in arrivals:
        arrival_times[arrival.id_team][arrival.id_puzzle] = arrival.timestamp.strftime("%H:%M")

    solve_times = defaultdict(dict)
    for solve in solves:
        solve_times[solve.id_team][solve.id_puzzle] = solve.timestamp.strftime("%H:%M")

    return render("progress_table.html", puzzles=puzzles, teams=teams, arrival_times=arrival_times, solve_times=solve_times)

