import csv

from flask import request, redirect, Blueprint, flash

from db_model import Puzzlehunt, db, Team
from helpers import render, admin_required

teams_csv_import = Blueprint('teams_csv_import', __name__, template_folder='templates', static_folder='static')


@teams_csv_import.route('/teams/csv_import', methods=("GET", "POST"))
@admin_required
def teams_import():
    if request.method == "POST":
        try:
            puzzlehunt_id = Puzzlehunt.get_current_id()

            # name,password,phone,note
            reader = csv.DictReader(request.form['teams_csv'].splitlines(), restval="")
            for row in reader:
                team = Team(puzzlehunt_id, row["name"], row["password"],
                            row["phone"] if "phone" in row else "",
                            row["note"] if "note" in row else "")
                db.session.add(team)

            db.session.commit()
        except KeyError as e:
            flash(f'Chyba při importu: chybí sloupec {e}.', "warning")
        except ValueError as e:
            flash(f'Chyba při importu: {e}', "warning")

        return redirect(f"/teams")
    return render("teams_csv_import.html")
