from db_model import Puzzlehunt, Settings
from tmm_webinfo import db, app

with app.app_context():
    db.create_all()

    if db.session.query(Puzzlehunt).first() is None:
        default_puzzlehunt = Puzzlehunt("Šifrovačka")
        db.session.add(default_puzzlehunt)
        db.session.commit()
        current_puzzlehunt = Settings("current_puzzlehunt")
        current_puzzlehunt.value = str(default_puzzlehunt.id_puzzlehunt)
        db.session.add(current_puzzlehunt)
        db.session.commit()
