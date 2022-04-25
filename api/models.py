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
