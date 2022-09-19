import csv

from flask import request, redirect, Blueprint, flash

from db_model import Puzzlehunt, db, PuzzlehuntSettings, Puzzle, ArrivalCode, SolutionCode, Hint, PuzzlePrerequisite
from helpers import render, admin_required

csv_import = Blueprint('csv_import', __name__, template_folder='templates', static_folder='static')


@csv_import.route('/csv_import', methods=("GET", "POST"))
@admin_required
def puzzlehunts_new():
    if request.method == "POST":
        try:
            puzzlehunt = Puzzlehunt(request.form["puzzlehunt"])
            db.session.add(puzzlehunt)
            db.session.flush()

            minutes_to_hint_setting = PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "minutes_to_hint")
            minutes_to_hint_setting.value = request.form["minutes_to_hint"]
            minutes_to_hint = int(minutes_to_hint_setting.value)
            db.session.add(minutes_to_hint_setting)
            hints_are_ordered = PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "hints_are_ordered")
            hints_are_ordered.value = "True"
            db.session.add(hints_are_ordered)

            puzzles = {}
            # order,puzzle,arrival_code,solution_code,solution_message,hint_1,hint_2,prerequisites
            reader = csv.DictReader(request.form['puzzlehunt_csv'].splitlines())
            for row in reader:
                order = int(row['order'])
                puzzle = Puzzle(puzzlehunt.id_puzzlehunt, row['puzzle'], "", order)
                db.session.add(puzzle)
                db.session.flush()
                puzzles[order] = puzzle.id_puzzle

                db.session.add(ArrivalCode(puzzle.id_puzzle, row['arrival_code'], ""))
                db.session.add(SolutionCode(puzzle.id_puzzle, row['solution_code'], row['solution_message']))
                db.session.add(Hint(puzzle.id_puzzle, 1, minutes_to_hint, row['hint_1']))
                db.session.add(Hint(puzzle.id_puzzle, 2, minutes_to_hint, row['hint_2']))

                prerequisites = [int(x) for x in row['prerequisites'].split(',') if x]
                for prerequisite in prerequisites:
                    if prerequisite not in puzzles:
                        flash(f'Chyba u šifry "{puzzle.puzzle}". Prerekvizity mohou být jen předchozí šifry.', "warning")
                    else:
                        db.session.add(PuzzlePrerequisite(puzzles[prerequisite], puzzle.id_puzzle))

            db.session.commit()
        except KeyError as e:
            flash(f'Chyba při importu: chybí sloupec {e}.', "warning")
        except ValueError as e:
            flash(f'Chyba při importu: {e}', "warning")

        return redirect(f"/puzzlehunts")
    return render("csv_import.html")
