from collections import defaultdict
from datetime import timedelta
from typing import List

from flask import Blueprint, redirect, flash, request
from sqlalchemy import func
from scipy.stats import rankdata

from db_model import Team, TeamUsedHint, Hint, TeamSubmittedCode, Puzzlehunt, db, PuzzlehuntSettings
from helpers import render, admin_required, format_time

results_table = Blueprint('results_table', __name__, template_folder='templates', static_folder='static')


def format_times(times: dict) -> dict:
    result = dict()
    for key in times:
        result[key] = format_time(times[key])
    return result


@results_table.route('/results')
@admin_required
def progress():
    current_puzzlehunt = Puzzlehunt.get_current()
    puzzlehunt_settings = current_puzzlehunt.get_settings()
    if "start_code" not in puzzlehunt_settings:
        flash("Před zobrazením výsledků je potřeba nastavit kód pro start", "danger")
        return redirect(f'/puzzlehunts/{current_puzzlehunt.id_puzzlehunt}')
    if "finish_code" not in puzzlehunt_settings:
        flash("Před zobrazením výsledků je potřeba nastavit kód pro cíl", "danger")
        return redirect(f'/puzzlehunts/{Puzzlehunt.get_current_id()}')
    start_code = int(puzzlehunt_settings["start_code"].value)
    finish_code = int(puzzlehunt_settings["finish_code"].value)

    teams: List[Team] = Team.query.filter_by(id_puzzlehunt=current_puzzlehunt.id_puzzlehunt).order_by(Team.name).all()
    team_ids_query = Team.query.filter_by(id_puzzlehunt=current_puzzlehunt.id_puzzlehunt).with_entities(Team.id_team)

    hints_used: List[int] = TeamUsedHint.query\
        .filter(TeamUsedHint.id_team.in_(team_ids_query))\
        .join(Hint)\
        .with_entities(TeamUsedHint.id_team, Hint.id_puzzle, func.count(Hint.id_hint))\
        .group_by(TeamUsedHint.id_team, Hint.id_puzzle)\
        .all()

    hints = defaultdict(int)
    for id_team, _, hint_count in hints_used:
        hints[id_team] += hint_count

    hint_penalty = 0
    try:
        hint_penalty = int(puzzlehunt_settings["hint_penalty"].value)
    except (KeyError, ValueError):
        flash("Penalizace za nápovědy není nastavena, zobrazují se výsledky s nulovou penalizací.", "warning")

    start_times = {}
    for start in TeamSubmittedCode.query \
            .filter_by(id_code=start_code) \
            .filter(TeamSubmittedCode.id_team.in_(team_ids_query)):
        start_times[start.id_team] = start.timestamp

    finish_times = {}
    for finish in TeamSubmittedCode.query\
            .filter_by(id_code=finish_code)\
            .filter(TeamSubmittedCode.id_team.in_(team_ids_query)):
        finish_times[finish.id_team] = finish.timestamp

    # compute times and penalties
    times = {}
    penalties = {}
    total_times = {}
    for team in teams:
        if team.id_team in start_times and team.id_team in finish_times:
            times[team.id_team] = finish_times[team.id_team] - start_times[team.id_team]

        penalties[team.id_team] = timedelta(minutes=hints[team.id_team] * hint_penalty)
        if team.id_team in times:
            total_times[team.id_team] = times[team.id_team] + penalties[team.id_team]

    # compute ranks
    ranks = {
        id_team: rank
        for id_team, rank
        in zip(times, rankdata(list(times.values()), method='dense'))
    }
    total_ranks = {
        id_team: rank
        for id_team, rank
        in zip(total_times, rankdata(list(total_times.values()), method='dense'))
    }

    # sort teams by total rank (not finished teams are last)
    teams = sorted(teams, key=lambda t: total_ranks[t.id_team] if t.id_team in total_ranks else len(teams))

    return render("results_table.html", fluid=True, teams=teams, start_times=format_times(start_times), finish_times=format_times(finish_times), hints=hints, times=format_times(times), penalties=format_times(penalties), total_times=format_times(total_times), ranks=ranks, total_ranks=total_ranks, hint_penalty=hint_penalty)


@results_table.route('/results/hint_penalty', methods=("POST",))
@admin_required
def set_hint_penalty():
    current_puzzlehunt_id = Puzzlehunt.get_current_id()
    puzzlehunt_settings = Puzzlehunt.get_settings_for_id(current_puzzlehunt_id)
    hint_penalty = puzzlehunt_settings.get("hint_penalty",
                                           PuzzlehuntSettings(current_puzzlehunt_id, "hint_penalty"))
    hint_penalty.value = request.form["hint_penalty"]
    db.session.add(hint_penalty)
    db.session.commit()
    flash(f"Penalizace za nápovědy nastavena na {request.form['hint_penalty']} minut.", "success")
    return redirect("/results")
