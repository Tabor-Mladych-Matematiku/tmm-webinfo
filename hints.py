from flask import request, redirect, flash, Blueprint

from db_model import Puzzle, db, Hint, Puzzlehunt
from helpers import render, admin_required

hints = Blueprint('hints', __name__, template_folder='templates', static_folder='static')


def get_hints(id_puzzle):
    return Hint.query.filter_by(id_puzzle=id_puzzle).all()


@hints.route('/puzzles/<id_puzzle>/hints/new', methods=("GET", "POST"))
@admin_required
def hints_new(id_puzzle):
    puzzle = Puzzle.query.get(id_puzzle)

    if request.method == "POST":
        hint = Hint(id_puzzle, request.form['order'], request.form['minutes_to_open'], request.form['hint'])
        db.session.add(hint)
        db.session.commit()
        return redirect(f"/puzzles/{id_puzzle}")
    else:
        order = Hint.query.filter_by(id_puzzle=id_puzzle).count() + 1
        puzzlehunt_settings = Puzzlehunt.get_settings_for_id(puzzle.id_puzzlehunt)
        default_minutes_to_open = puzzlehunt_settings["minutes_to_hint"].value if "minutes_to_hint" in puzzlehunt_settings else ""
        return render("hint_edit.html", puzzle=puzzle, order=order, minutes_to_open=default_minutes_to_open)


@hints.route('/puzzles/<id_puzzle>/hints/<id_hint>', methods=("GET", "POST"))
@admin_required
def hints_edit(id_puzzle, id_hint):
    puzzle = Puzzle.query.get(id_puzzle)
    if puzzle is None:
        flash(f"Šifra s id_puzzle={id_puzzle} neexistuje.", "warning")
        return redirect("/puzzles")
    hint = Hint.query.get(id_hint)
    if hint is None:
        flash(f"Nápověda s id_hint={id_hint} neexistuje.", "warning")
        return redirect(f"/puzzles/{id_puzzle}")

    if request.method == "POST":
        hint.order = request.form["order"]
        hint.minutes_to_open = request.form["minutes_to_open"]
        hint.hint = request.form["hint"]
        db.session.add(hint)
        db.session.commit()
        return redirect(f"/puzzles/{id_puzzle}")
    else:
        return render("hint_edit.html", puzzle=puzzle, hint=hint)


@hints.route('/puzzles/<id_puzzle>/hints/<id_hint>/delete', methods=("POST",))
@admin_required
def prerequisites_delete(id_puzzle, id_hint):
    puzzle = Puzzle.query.get(id_puzzle)
    if puzzle is None:
        flash(f"Šifra s id_puzzle={id_puzzle} neexistuje.", "warning")
        return redirect("/puzzles")
    hint = Hint.query.get(id_hint)
    if hint is None:
        flash(f"Nápověda s id_hint={id_hint} neexistuje.", "warning")
        return redirect(f"/puzzles/{id_puzzle}")

    db.session.delete(hint)
    db.session.commit()
    flash(f'{hint.order}. nápověda k šifře "{puzzle.puzzle}" smazána.', "success")
    return redirect(f"/puzzles/{id_puzzle}")
