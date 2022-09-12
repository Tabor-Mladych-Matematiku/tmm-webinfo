from flask import redirect, url_for, request, flash, render_template, Blueprint
from flask_bcrypt import check_password_hash
from flask_login import current_user, login_user, login_required, logout_user

from config import config
from db_model import Admin, Team
from helpers import get_current_puzzlehunt, is_safe_url

login_blueprint = Blueprint('login', __name__, template_folder='templates', static_folder='static')


@login_blueprint.route('/login', methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('example'))

    user = ""
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]

        if user == "admin" and password == config['admin_password']:
            login_user(Admin(), remember=True)
            next_url = request.args.get('next')
            if next_url and is_safe_url(next_url):
                return redirect(next_url)
            return redirect('/')
        else:
            team: Team = Team.query.filter_by(name=user, id_puzzlehunt=get_current_puzzlehunt()).first()
            if team and check_password_hash(team.password, password):
                login_user(team)
                next_url = request.args.get('next')
                if next_url and is_safe_url(next_url):
                    return redirect(next_url)
                return redirect('/')
            else:
                flash(f"Neplatné přilašovací údaje.", "danger")

    return render_template("login.html", title="Přihlášení", user=user)


@login_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')
