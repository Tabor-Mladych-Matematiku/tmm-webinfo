from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_bcrypt import Bcrypt, check_password_hash

from db_model import db, Admin, Team, Settings, Puzzlehunt
from config import config

app = Flask(__name__)
app.secret_key = config['secret']
app.config["DEBUG"] = True

# Database configuration

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

# Login configuration

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login"
login_manager.login_message_category = "info"
login_manager.login_message = "Pro zobrazení stránky se přihlaste."


@login_manager.user_loader
def load_user(user_id):
    if user_id == "-1":
        return Admin()
    else:
        return Team.query.get(int(user_id))


bcrypt = Bcrypt()
bcrypt.init_app(app)

# Helpers


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


# Login routes


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


# Admin routes


@app.route('/example')
@login_required
def example():
    return render("example.html", title="Jinja and Flask")


@app.route('/puzzlehunts')
@login_required
def puzzlehunts():
    puzzlehunts = Puzzlehunt.query.all()
    current_puzzlehunt = get_current_puzzlehunt()
    return render("puzzlehunts.html", puzzlehunts=puzzlehunts, current_puzzlehunt=current_puzzlehunt)


@app.route('/puzzlehunts/new', methods=("GET", "POST"))
@login_required
def puzzlehunts_new():
    if request.method == "POST":
        puzzlehunt = Puzzlehunt(request.form["puzzlehunt"])
        db.session.add(puzzlehunt)
        db.session.commit()
        return redirect("/puzzlehunts")
    return render("puzzlehunt_edit.html")


@app.route('/puzzlehunts/<id_puzzlehunt>', methods=("GET", "POST"))
@login_required
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
        return render("puzzlehunt_edit.html", puzzlehunt=puzzlehunt)


@app.route('/puzzlehunts/<id_puzzlehunt>/activate', methods=("POST",))
@login_required
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


@app.route('/puzzlehunts/<id_puzzlehunt>/delete', methods=("POST",))
@login_required
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
    flash(f'šifrovačka "{puzzlehunt.puzzlehunt}" smazána.', "success")
    return redirect("/puzzlehunts")


# Team routes


@app.route('/')
@login_required
def index():
    return render("index.html", title="Jinja and Flask")
