from flask import request, redirect, flash, Blueprint

from codes import get_codes
from db_model import Puzzlehunt, db, Settings
from helpers import get_current_puzzlehunt, render, admin_required

puzzlehunts = Blueprint('puzzlehunts', __name__, template_folder='templates', static_folder='static')


@puzzlehunts.route('/puzzlehunts')
@admin_required
def puzzlehunts_list():
    puzzlehunts = Puzzlehunt.query.all()
    current_puzzlehunt = get_current_puzzlehunt()
    return render("puzzlehunts.html", puzzlehunts=puzzlehunts, current_puzzlehunt=current_puzzlehunt)


@puzzlehunts.route('/puzzlehunts/new', methods=("GET", "POST"))
@admin_required
def puzzlehunts_new():
    if request.method == "POST":
        puzzlehunt = Puzzlehunt(request.form["puzzlehunt"])
        db.session.add(puzzlehunt)
        db.session.commit()
        return redirect("/puzzlehunts")
    return render("puzzlehunt_edit.html")


@puzzlehunts.route('/puzzlehunts/<id_puzzlehunt>', methods=("GET", "POST"))
@admin_required
def puzzlehunts_edit(id_puzzlehunt):
    puzzlehunt = Puzzlehunt.query.get(id_puzzlehunt)
    if puzzlehunt is None:
        flash(f"Šifrovačka s id_puzzlehunt={id_puzzlehunt} neexistuje.", "warning")
        return redirect("/puzzlehunts")

    if request.method == "POST":
        puzzlehunt.puzzlehunt = request.form["puzzlehunt"]
        db.session.add(puzzlehunt)
        db.session.commit()
        return redirect("/puzzlehunts")
    else:
        return render("puzzlehunt_edit.html", puzzlehunt=puzzlehunt, codes=get_codes(id_puzzlehunt))


@puzzlehunts.route('/puzzlehunts/<id_puzzlehunt>/activate', methods=("POST",))
@admin_required
def puzzlehunts_activate(id_puzzlehunt):
    puzzlehunt = Puzzlehunt.query.get(id_puzzlehunt)
    if puzzlehunt is None:
        flash(f"Šifrovačka s id_puzzlehunt={id_puzzlehunt} neexistuje.", "warning")
    else:
        current_puzzlehunt_setting = Settings.query.get("current_puzzlehunt")
        if current_puzzlehunt_setting is None:
            current_puzzlehunt_setting = Settings("current_puzzlehunt")
        current_puzzlehunt_setting.value = str(id_puzzlehunt)
        db.session.add(current_puzzlehunt_setting)
        db.session.commit()
        flash(f'Aktivní šifrovačka nastavena na "{puzzlehunt.puzzlehunt}".', "success")
    return redirect("/puzzlehunts")


@puzzlehunts.route('/puzzlehunts/<id_puzzlehunt>/delete', methods=("POST",))
@admin_required
def puzzlehunts_delete(id_puzzlehunt):
    if id_puzzlehunt == str(get_current_puzzlehunt()):
        flash(f"Aktivní šifrovačku nelze smazat.", "warning")
        return redirect("/puzzlehunts")

    puzzlehunt = Puzzlehunt.query.get(id_puzzlehunt)
    if puzzlehunt is None:
        flash(f"Šifrovačka s id_puzzlehunt={id_puzzlehunt} neexistuje.", "warning")
        return redirect("/puzzlehunts")

    db.session.delete(puzzlehunt)
    db.session.commit()
    flash(f'Šifrovačka "{puzzlehunt.puzzlehunt}" smazána.', "success")
    return redirect("/puzzlehunts")
