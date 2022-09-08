from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Sifrovacka(db.Model):

    __tablename__ = "sifrovacky"

    id_sifrovacka = db.Column(db.Integer, primary_key=True)
    sifrovacka = db.Column(db.String(256))
