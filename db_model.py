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
        return False

    @property
    def id(self):
        return -1


class Tym(db.Model, User):

    __tablename__ = "tymy"

    id_tym = db.Column(db.Integer, primary_key=True)
    # id_sifrovacka = db.Column(db.Integer, db.ForeignKey("sifrovacky.id_sifrovacka"))
    jmeno = db.Column(db.String(256), nullable=False)
    heslo = db.Column(db.String(256), nullable=False)
    telefon = db.Column(db.String(256), nullable=True)

    @property
    def id(self):
        return -1


class Sifrovacka(db.Model):

    __tablename__ = "sifrovacky"

    id_sifrovacka = db.Column(db.Integer, primary_key=True)
    sifrovacka = db.Column(db.String(256))
