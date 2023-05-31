from datetime import timezone, timedelta
from functools import wraps
from urllib.parse import urlparse, urljoin

from flask import render_template, redirect, flash, request
from flask_login import current_user, login_required

from db_model import Puzzlehunt


def render(template, **kwargs):
    parameters = {
        "user": current_user,
        "current_puzzlehunt_name": Puzzlehunt.get_current().puzzlehunt
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
            flash("Tato stránka je dostupná pouze organizátorům.", "danger")
            return redirect("/")
        return func(*args, **kwargs)

    return login_required(decorated_view)


def is_safe_url(target):
    """
    Ensures that a redirect target will lead to the same server.
    Taken from: <https://web.archive.org/web/20120517003641/http://flask.pocoo.org/snippets/62/>
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def format_time(time):
    return time.strftime("%H:%M")
