import abc
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin):

    @property
    def is_admin(self):
        return False

    @property
    def id(self):
        return


class Admin(User):

    @property
    def is_admin(self):
        return True

    @property
    def id(self):
        return -1

    name = "admin"


class Team(db.Model, User):

    __tablename__ = "teams"

    id_team = db.Column(db.Integer, primary_key=True)
    # id_puzzlehunt = db.Column(db.Integer, db.ForeignKey("puzzlehunt.id_puzzlehunt"))
    name = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(256), nullable=True)

    @property
    def id(self):
        return self.id_team


class Settings(db.Model):

    __tablename__ = "settings"

    key = db.Column(db.String(256), primary_key=True)
    value = db.Column(db.Text)

    def __init__(self, key):
        self.key = key


class Puzzlehunt(db.Model):

    __tablename__ = "puzzlehunts"

    id_puzzlehunt = db.Column(db.Integer, primary_key=True)
    puzzlehunt = db.Column(db.String(256))

    def __init__(self, puzzlehunt):
        self.puzzlehunt = puzzlehunt