from flask_sqlalchemy import SQLAlchemy
import geoalchemy2 as ga2

db = SQLAlchemy()


class BoroModel(db.Model):
    __tablename__ = 'boro'
    the_geom = ga2.Column(ga2.Geography('MULTIPOLYGON'), nullable=False)
    boro_code = db.Column(db.INTEGER(), nullable=False, primary_key=True)
    boro_name = db.Column(db.VARCHAR(), nullable=False)
    shape_leng = db.Column(db.REAL(), nullable=False)
    shape_area = db.Column(db.REAL(), nullable=False)
    ntas = db.relationship('NTAModel', backref='boro', lazy=True)

class NTAModel(db.Model):
    __tablename__ = 'nta'
    the_geom = ga2.Column(ga2.Geography('MULTIPOLYGON'), nullable=False)
    borocode = db.Column(db.INTEGER(), db.ForeignKey('boro.boro_code'), nullable=False)
    countyfips = db.Column(db.INTEGER(), nullable=False)
    nta2020 = db.Column(db.VARCHAR(6), nullable=False, primary_key=True)
    ntaname = db.Column(db.VARCHAR(), nullable=False, unique=True)
    ntaabbrev = db.Column(db.VARCHAR(), nullable=False, unique=True)
    ntatype = db.Column(db.INTEGER(), nullable=False)
    cdta2020 = db.Column(db.VARCHAR(6), nullable=False)
    cdtaname = db.Column(db.VARCHAR(), nullable=False)
    shape_leng = db.Column(db.REAL(), nullable=False)
    shape_area = db.Column(db.REAL(), nullable=False)
