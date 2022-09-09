from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_bcrypt import Bcrypt, check_password_hash

from db_model import db, Admin, Team
from config import config

app = Flask(__name__)
app.secret_key = config['secret']

app.config["DEBUG"] = True

if 'db' in config:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username=config['db']['user'],
        password=config['db']['password'],
        hostname=config['db']['hostname'],
        databasename=config['db']['database'],
    )
else:
    SQLALCHEMY_DATABASE_URI = "sqlite:///test.sqlite"

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    if user_id == "-1":
        return Admin()
    else:
        return Team.query.get(int(user_id))


bcrypt = Bcrypt()
bcrypt.init_app(app)


def render(template, **kwargs):
    parameters = {
        "team": current_user
    }
    parameters.update(kwargs)
    return render_template(template, **parameters)


@app.route('/login', methods=("GET", "POST"))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('example'))

    user = ""
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]

        if user == "admin" and password == config['admin_password']:
            login_user(Admin(), remember=True)
            return redirect(url_for('example'))
        else:
            team: Team = Team.query.filter_by(name=user).first()
            if team and check_password_hash(team.password, password):
                login_user(team)
                return redirect(url_for('example'))
            else:
                flash(f"Neplatné přilašovací údaje.", "danger")

    return render_template("login.html", title="Přihlášení", user=user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/example')
@login_required
def example():
    return render("example.html", title="Jinja and Flask")


@app.route('/')
@login_required
def index():
    return render("index.html", title="Jinja and Flask")
