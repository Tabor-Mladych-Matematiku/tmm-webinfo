from flask import render_template
from flask_login import current_user

from db_model import Settings


def get_current_puzzlehunt():
    current_puzzlehunt = Settings.query.get("current_puzzlehunt")
    if current_puzzlehunt is not None:
        return int(current_puzzlehunt.value)
    return None


def render(template, **kwargs):
    parameters = {
        "user": current_user
    }
    parameters.update(kwargs)
    return render_template(template, **parameters)
