import abc

from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()


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
    id_puzzlehunt = db.Column(db.Integer, db.ForeignKey("puzzlehunts.id_puzzlehunt"))
    name = db.Column(db.String(256), nullable=False)
    password = db.Column(db.String(256), nullable=False)
    phone = db.Column(db.String(256), nullable=True)
    note = db.Column(db.Text, nullable=True)

    @property
    def id(self):
        return self.id_team

    def __init__(self, current_puzzlehunt, name, password_plain, phone, note):
        self.id_puzzlehunt = current_puzzlehunt
        self.name = name
        self.set_password(password_plain)
        self.phone = phone
        self.note = note

    def set_password(self, password_plain):
        self.password = bcrypt.generate_password_hash(password_plain)


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


class Puzzle(db.Model):

    __tablename__ = "puzzles"

    id_puzzle = db.Column(db.Integer, primary_key=True)
    id_puzzlehunt = db.Column(db.Integer, db.ForeignKey("puzzlehunts.id_puzzlehunt"))
    puzzle = db.Column(db.String(256))
    assignment = db.Column(db.Text)
    order = db.Column(db.Integer)

    def __init__(self, current_puzzlehunt, puzzle, assignment, order):
        self.id_puzzlehunt = current_puzzlehunt
        self.puzzle = puzzle
        self.assignment = assignment
        self.order = order

    def get_prerequisites(self):
        p = Puzzle.query.join(PuzzlePrerequisite, Puzzle.id_puzzle == PuzzlePrerequisite.id_previous_puzzle)\
            .filter_by(id_new_puzzle=self.id_puzzle).all()
        return p


class PuzzlePrerequisite(db.Model):

    __tablename__ = "puzzle_prerequisites"

    id_previous_puzzle = db.Column(db.Integer, db.ForeignKey("puzzles.id_puzzle"), primary_key=True)
    id_new_puzzle = db.Column(db.Integer, db.ForeignKey("puzzles.id_puzzle"), primary_key=True)

    def __init__(self, id_previous_puzzle, id_new_puzzle):
        self.id_previous_puzzle = id_previous_puzzle
        self.id_new_puzzle = id_new_puzzle
