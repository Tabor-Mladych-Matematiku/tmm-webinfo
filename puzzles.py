from flask import request, redirect, flash, Blueprint
from flask_login import login_required

from db_model import Puzzle, db
from helpers import render, get_current_puzzlehunt

puzzles = Blueprint('puzzles', __name__, template_folder='templates', static_folder='static')


@puzzles.route('/puzzles')
@login_required
def puzzles_list():
    puzzles = Puzzle.query.filter_by(id_puzzlehunt=get_current_puzzlehunt()).order_by(Puzzle.order).all()
    return render("puzzles.html", puzzles=puzzles)


@puzzles.route('/puzzles/new', methods=("GET", "POST"))
@login_required
def puzzles_new():
    if request.method == "POST":
        puzzle = Puzzle(get_current_puzzlehunt(), request.form["puzzle"], request.form["assignment"], request.form["order"])
        db.session.add(puzzle)
        db.session.commit()
        return redirect("/puzzles")
    order = Puzzle.query.filter_by(id_puzzlehunt=get_current_puzzlehunt()).count() + 1
    return render("puzzle_edit.html", order=order)


@puzzles.route('/puzzles/<id_puzzle>', methods=("GET", "POST"))
@login_required
def puzzles_edit(id_puzzle):
    puzzle = Puzzle.query.get(id_puzzle)
    if puzzle is None:
        flash(f"Šifra s id_puzzle={id_puzzle} neexistuje.", "warning")
        return redirect("/puzzles")

    if request.method == "POST":
        puzzle.puzzle = request.form["puzzle"]
        puzzle.assignment = request.form["assignment"]
        puzzle.order = request.form["order"]
        db.session.add(puzzle)
        db.session.commit()
        return redirect("/puzzles")
    else:
        return render("puzzle_edit.html", puzzle=puzzle)


@puzzles.route('/puzzles/<id_puzzle>/delete', methods=("POST",))
@login_required
def puzzles_delete(id_puzzle):
    puzzle = Puzzle.query.get(id_puzzle)
    if puzzle is None:
        flash(f"Šifra s id_puzzle={id_puzzle} neexistuje.", "warning")
        return redirect("/puzzles")

    db.session.delete(puzzle)
    db.session.commit()
    flash(f'Šifra "{puzzle.puzzle}" smazána.', "success")
    return redirect("/puzzles")
