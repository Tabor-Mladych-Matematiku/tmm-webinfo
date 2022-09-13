from flask import Flask
from flask_login import LoginManager

from db_model import db, Admin, Team, bcrypt
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
bcrypt.init_app(app)

# Login configuration

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_view = "login.login"
login_manager.login_message_category = "info"
login_manager.login_message = "Pro zobrazení stránky se přihlaste."


@login_manager.user_loader
def load_user(user_id):
    if user_id == "-1":
        return Admin()
    else:
        return Team.query.get(int(user_id))


from login import login_blueprint
app.register_blueprint(login_blueprint)


# Admin routes


from puzzlehunts import puzzlehunts
app.register_blueprint(puzzlehunts)
from puzzles import puzzles
app.register_blueprint(puzzles)
from teams import teams
app.register_blueprint(teams)
from codes import codes
app.register_blueprint(codes)
from hints import hints
app.register_blueprint(hints)
from progress_table import progress_table
app.register_blueprint(progress_table)


# Team routes


from journey import journey
app.register_blueprint(journey)
from history import history_blueprint
app.register_blueprint(history_blueprint)
