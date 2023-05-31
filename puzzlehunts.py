from flask import request, redirect, flash, Blueprint

from codes import get_codes
from db_model import Puzzlehunt, db, Settings, PuzzlehuntSettings
from helpers import render, admin_required

puzzlehunts = Blueprint('puzzlehunts', __name__, template_folder='templates', static_folder='static')


@puzzlehunts.route('/puzzlehunts')
@admin_required
def puzzlehunts_list():
    puzzlehunts = Puzzlehunt.query.all()
    current_puzzlehunt = Puzzlehunt.get_current_id()
    return render("puzzlehunts.html", puzzlehunts=puzzlehunts, current_puzzlehunt=current_puzzlehunt)


@puzzlehunts.route('/puzzlehunts/new', methods=("GET", "POST"))
@admin_required
def puzzlehunts_new():
    if request.method == "POST":
        puzzlehunt = Puzzlehunt(request.form["puzzlehunt"])
        db.session.add(puzzlehunt)
        db.session.flush()

        minutes_to_hint = PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "minutes_to_hint")
        minutes_to_hint.value = request.form["minutes_to_hint"]
        db.session.add(minutes_to_hint)
        hints_are_ordered = PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "hints_are_ordered")
        hints_are_ordered.value = str("hints_are_ordered" in request.form)
        db.session.add(hints_are_ordered)
        hint_penalty = PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "hint_penalty")
        hint_penalty.value = request.form["hint_penalty"]
        db.session.add(hint_penalty)
        db.session.commit()

        return redirect(f"/puzzlehunts/{puzzlehunt.id_puzzlehunt}")
    return render("puzzlehunt_edit.html")


@puzzlehunts.route('/puzzlehunts/<id_puzzlehunt>', methods=("GET", "POST"))
@admin_required
def puzzlehunts_edit(id_puzzlehunt):
    puzzlehunt = Puzzlehunt.query.get(id_puzzlehunt)
    if puzzlehunt is None:
        flash(f"Šifrovačka s id_puzzlehunt={id_puzzlehunt} neexistuje.", "warning")
        return redirect("/puzzlehunts")
    puzzlehunt_settings = Puzzlehunt.get_settings_for_id(id_puzzlehunt)

    if request.method == "POST":
        puzzlehunt.puzzlehunt = request.form["puzzlehunt"]
        db.session.add(puzzlehunt)

        minutes_to_hint = puzzlehunt_settings.get("minutes_to_hint",
                                                  PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "minutes_to_hint"))
        minutes_to_hint.value = request.form["minutes_to_hint"]
        db.session.add(minutes_to_hint)

        hints_are_ordered = puzzlehunt_settings.get("hints_are_ordered",
                                                    PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "hints_are_ordered"))
        hints_are_ordered.value = str("hints_are_ordered" in request.form)
        db.session.add(hints_are_ordered)

        hint_penalty = puzzlehunt_settings.get("hint_penalty",
                                               PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "hint_penalty"))
        hint_penalty.value = request.form["hint_penalty"]
        db.session.add(hint_penalty)

        finish_code = puzzlehunt_settings.get("finish_code",
                                              PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "finish_code"))
        finish_code.value = request.form["finish_code"]
        db.session.add(finish_code)

        start_code = puzzlehunt_settings.get("start_code",
                                             PuzzlehuntSettings(puzzlehunt.id_puzzlehunt, "start_code"))
        start_code.value = request.form["start_code"]
        db.session.add(start_code)

        db.session.commit()
        return redirect("/puzzlehunts")
    else:
        return render("puzzlehunt_edit.html", puzzlehunt=puzzlehunt, codes=get_codes(id_puzzlehunt),
                      puzzlehunt_settings=puzzlehunt_settings)


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
    if id_puzzlehunt == str(Puzzlehunt.get_current_id()):
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
