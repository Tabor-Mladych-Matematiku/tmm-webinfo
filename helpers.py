from functools import wraps

from flask import render_template, redirect, flash
from flask_login import current_user, login_required

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


def admin_required(func):
    """
    If you decorate a view with this, it will ensure that the current user is admin.
    """

    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin:
            flash(f"Tato stránka je dostupná pouze organizátorům.", "danger")
            return redirect("/")
        return func(*args, **kwargs)

    return login_required(decorated_view)
