from flask import request, redirect, flash, Blueprint

from db_model import Puzzle, db, Code, ArrivalCode, SolutionCode
from helpers import render, admin_required

codes = Blueprint('codes', __name__, template_folder='templates', static_folder='static')


# Puzzlehunt codes


def get_codes(id_puzzlehunt):
    return Code.query.filter_by(id_puzzlehunt=id_puzzlehunt).all()


@codes.route('/puzzlehunts/<id_puzzlehunt>/codes/new', methods=("GET", "POST"))
@admin_required
def codes_new(id_puzzlehunt):
    if request.method == "POST":
        code = Code(id_puzzlehunt, request.form["code"], request.form["message"])
        db.session.add(code)
        db.session.commit()
        return redirect(f"/puzzlehunts/{id_puzzlehunt}")
    return render("code_edit.html", heading="Přidat kód do šifrovačky", back_url=f"/puzzlehunts/{id_puzzlehunt}")


@codes.route('/puzzlehunts/<id_puzzlehunt>/codes/<id_code>', methods=("GET", "POST"))
@admin_required
def codes_edit(id_puzzlehunt, id_code):
    code = Code.query.get(id_code)
    if code is None:
        flash(f"Kód s id_code={id_code} neexistuje.", "warning")
        return redirect(f"/puzzlehunts/{id_puzzlehunt}")

    if request.method == "POST":
        code.code = request.form["code"]
        code.message = request.form["message"]
        db.session.add(code)
        db.session.commit()
        return redirect(f"/puzzlehunts/{id_puzzlehunt}")
    else:
        return render("code_edit.html", heading="Upravit kód", back_url=f"/puzzlehunts/{id_puzzlehunt}", code=code)


@codes.route('/puzzlehunts/<id_puzzlehunt>/codes/<id_code>/delete', methods=("POST",))
@admin_required
def codes_delete(id_puzzlehunt, id_code):
    code = Code.query.get(id_code)
    if code is None:
        flash(f"Kód s id_code={id_code} neexistuje.", "warning")
        return redirect(f"/puzzlehunts/{id_puzzlehunt}")

    db.session.delete(code)
    db.session.commit()
    flash(f'Kód "{code.code}" smazán.', "success")
    return redirect(f"/puzzlehunts/{id_puzzlehunt}")


# Arrival codes


def get_arrival_codes(id_puzzle):
    return ArrivalCode.query.filter_by(id_puzzle=id_puzzle).all()


@codes.route('/puzzles/<id_puzzle>/arrival_codes/new', methods=("GET", "POST"))
@admin_required
def arrival_codes_new(id_puzzle):
    puzzle = Puzzle.query.get(id_puzzle)
    if puzzle is None:
        flash(f"Šifra s id_puzzle={id_puzzle} neexistuje.", "warning")
        return redirect("/puzzles")

    if request.method == "POST":
        code = ArrivalCode(id_puzzle, request.form["code"], request.form["message"])
        db.session.add(code)
        db.session.commit()
        return redirect(f"/puzzles/{id_puzzle}")
    return render("code_edit.html", heading="Přidat kód na otevření šifry", back_url=f"/puzzles/{id_puzzle}", puzzle_name=puzzle.puzzle)


@codes.route('/puzzles/<id_puzzle>/arrival_codes/<id_arrival_code>', methods=("GET", "POST"))
@admin_required
def arrival_codes_edit(id_puzzle, id_arrival_code):
    puzzle = Puzzle.query.get(id_puzzle)
    if puzzle is None:
        flash(f"Šifra s id_puzzle={id_puzzle} neexistuje.", "warning")
        return redirect("/puzzles")
    arrival_code = ArrivalCode.query.get(id_arrival_code)
    if arrival_code is None:
        flash(f"Kód s id_arrival_code={id_arrival_code} neexistuje.", "warning")
        return redirect(f"/puzzles/{id_puzzle}")

    if request.method == "POST":
        arrival_code.code = request.form["code"]
        arrival_code.message = request.form["message"]
        db.session.add(arrival_code)
        db.session.commit()
        return redirect(f"/puzzles/{id_puzzle}")
    else:
        return render("code_edit.html", heading="Upravit kód", back_url=f"/puzzles/{id_puzzle}", code=arrival_code, puzzle_name=puzzle.puzzle)


@codes.route('/puzzles/<id_puzzle>/arrival_codes/<id_arrival_code>/delete', methods=("POST",))
@admin_required
def arrival_codes_delete(id_puzzle, id_arrival_code):
    arrival_code = ArrivalCode.query.get(id_arrival_code)
    if arrival_code is None:
        flash(f"Kód s id_arrival_code={id_arrival_code} neexistuje.", "warning")
        return redirect(f"/puzzles/{id_puzzle}")

    db.session.delete(arrival_code)
    db.session.commit()
    flash(f'Kód "{arrival_code.code}" smazán.', "success")
    return redirect(f"/puzzles/{id_puzzle}")


# Solution codes


def get_solution_codes(id_puzzle):
    return SolutionCode.query.filter_by(id_puzzle=id_puzzle).all()


@codes.route('/puzzles/<id_puzzle>/solution_codes/new', methods=("GET", "POST"))
@admin_required
def solution_codes_new(id_puzzle):
    puzzle = Puzzle.query.get(id_puzzle)
    if puzzle is None:
        flash(f"Šifra s id_puzzle={id_puzzle} neexistuje.", "warning")
        return redirect("/puzzles")

    if request.method == "POST":
        code = SolutionCode(id_puzzle, request.form["code"], request.form["message"])
        db.session.add(code)
        db.session.commit()
        return redirect(f"/puzzles/{id_puzzle}")
    return render("code_edit.html", heading="Přidat řešení šifry", back_url=f"/puzzles/{id_puzzle}", puzzle_name=puzzle.puzzle)


@codes.route('/puzzles/<id_puzzle>/solution_codes/<id_solution_code>', methods=("GET", "POST"))
@admin_required
def solution_codes_edit(id_puzzle, id_solution_code):
    puzzle = Puzzle.query.get(id_puzzle)
    if puzzle is None:
        flash(f"Šifra s id_puzzle={id_puzzle} neexistuje.", "warning")
        return redirect("/puzzles")
    solution_code = SolutionCode.query.get(id_solution_code)
    if solution_code is None:
        flash(f"Řešení s id_solution_code={id_solution_code} neexistuje.", "warning")
        return redirect(f"/puzzles/{id_puzzle}")

    if request.method == "POST":
        solution_code.code = request.form["code"]
        solution_code.message = request.form["message"]
        db.session.add(solution_code)
        db.session.commit()
        return redirect(f"/puzzles/{id_puzzle}")
    else:
        return render("code_edit.html", heading="Upravit řešení", back_url=f"/puzzles/{id_puzzle}", code=solution_code, puzzle_name=puzzle.puzzle)


@codes.route('/puzzles/<id_puzzle>/solution_codes/<id_solution_code>/delete', methods=("POST",))
@admin_required
def solution_codes_delete(id_puzzle, id_solution_code):
    solution_code = SolutionCode.query.get(id_solution_code)
    if solution_code is None:
        flash(f"Řešení s id_solution_code={id_solution_code} neexistuje.", "warning")
        return redirect(f"/puzzles/{id_puzzle}")

    db.session.delete(solution_code)
    db.session.commit()
    flash(f'Řešení "{solution_code.code}" smazáno.', "success")
    return redirect(f"/puzzles/{id_puzzle}")

