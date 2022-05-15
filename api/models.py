from dataclasses import dataclass
from datetime import date, time
from flask_sqlalchemy import SQLAlchemy
import geoalchemy2 as ga2
from geoalchemy2 import WKBElement
from typing import Optional

db = SQLAlchemy()

h3_nta2020 = db.Table('h3_nta2020',
                      db.Column('h3_index', db.BIGINT(), db.ForeignKey('h3.h3_index'), nullable=False),
                      db.Column('nta2020_id', db.VARCHAR(6), db.ForeignKey('nta2020.id'), nullable=False),
                      db.PrimaryKeyConstraint('h3_index', 'nta2020_id'))


@dataclass
class Boro(db.Model):
    id: int
    name: str
    representative_point: tuple[float]
    centroid: tuple[float]
    bounds: tuple[tuple[float]]
    geometry: WKBElement
    land_geometry: WKBElement

    __tablename__ = 'boro'
    id = db.Column(db.INTEGER(), nullable=False, primary_key=True)
    name = db.Column(db.VARCHAR(), nullable=False)
    representative_point = db.Column(db.ARRAY(db.REAL(), as_tuple=True))
    centroid = db.Column(db.ARRAY(db.REAL(), as_tuple=True))
    bounds = db.Column(db.ARRAY(db.REAL(), as_tuple=True, dimensions=2))
    geometry = ga2.Column(ga2.Geometry(), nullable=False)
    land_geometry = ga2.Column(ga2.Geometry(), nullable=False)
    nta2020s = db.relationship('NTA2020', backref='boro', lazy=True, viewonly=True)


@dataclass
class NTA2020(db.Model):
    id: int
    name: Optional[str]
    boro_id: int
    representative_point: tuple[float]
    centroid: tuple[float]
    bounds: tuple[tuple[float]]
    geometry: WKBElement

    __tablename__ = 'nta2020'
    id = db.Column(db.VARCHAR(6), nullable=False, primary_key=True)
    name = db.Column(db.VARCHAR(), unique=True)
    boro_id = db.Column(db.INTEGER(), db.ForeignKey('boro.id'), nullable=False)
    representative_point = db.Column(db.ARRAY(db.REAL(), as_tuple=True))
    centroid = db.Column(db.ARRAY(db.REAL(), as_tuple=True))
    bounds = db.Column(db.ARRAY(db.REAL(), as_tuple=True, dimensions=2))
    geometry = ga2.Column(ga2.Geometry())
    h3s = db.relationship('H3', secondary=h3_nta2020, backref='h3_nta2020', viewonly=True)


@dataclass
class H3(db.Model):
    h3_index: int
    only_water: bool
    centroid: tuple[float]
    geometry: WKBElement

    __tablename__ = 'h3'
    h3_index = db.Column(db.BIGINT(), nullable=False, primary_key=True)
    only_water = db.Column(db.BOOLEAN(), nullable=False)
    centroid = db.Column(db.ARRAY(db.REAL(), as_tuple=True))
    geometry = ga2.Column(ga2.Geometry('POLYGON'), nullable=False)
    nta2020s = db.relationship('NTA2020', secondary=h3_nta2020, backref='h3_nta2020', viewonly=True)


@dataclass
class Person(db.Model):
    id: int
    collision_id: int
    vehicle_id: Optional[int]
    dangling_vehicle_id: Optional[int]
    type: Optional[str]
    injury: Optional[str]
    age: Optional[int]
    ejection: Optional[str]
    emotional_status: Optional[str]
    bodily_injury: Optional[str]
    position_in_vehicle: Optional[str]
    safety_equipment: Optional[str]
    location: Optional[str]
    action: Optional[str]
    complaint: Optional[str]
    role: Optional[str]
    contributing_factors: tuple[str]
    sex: Optional[str]

    __tablename__ = 'person'
    id = db.Column(db.BIGINT(), nullable=False, primary_key=True)
    collision_id = db.Column(db.BIGINT(), db.ForeignKey('collision.id'), nullable=False)
    vehicle_id = db.Column(db.BIGINT(), db.ForeignKey('vehicle.id'))
    dangling_vehicle_id = db.Column(db.BIGINT())
    type = db.Column(db.VARCHAR())
    injury = db.Column(db.VARCHAR())
    age = db.Column(db.INTEGER())
    ejection = db.Column(db.VARCHAR())
    emotional_status = db.Column(db.VARCHAR())
    bodily_injury = db.Column(db.VARCHAR())
    position_in_vehicle = db.Column(db.VARCHAR())
    safety_equipment = db.Column(db.VARCHAR())
    location = db.Column(db.VARCHAR())
    action = db.Column(db.VARCHAR())
    complaint = db.Column(db.VARCHAR())
    role = db.Column(db.VARCHAR())
    contributing_factors = db.Column(db.ARRAY(db.VARCHAR(), as_tuple=True))
    sex = db.Column(db.VARCHAR())


@dataclass
class Vehicle(db.Model):
    id: int
    collision_id: int
    state_registration: Optional[str]
    type: Optional[str]
    make: Optional[str]
    model: Optional[str]
    year: Optional[int]
    travel_direction: Optional[str]
    occupants: Optional[int]
    driver_sex: Optional[str]
    driver_license_status: Optional[str]
    driver_license_jurisdiction: Optional[str]
    pre_crash: Optional[str]
    point_of_impact: Optional[str]
    damages: tuple[str]
    public_property_damage: Optional[str]
    public_property_damage_type: Optional[str]
    contributing_factors: tuple[str]
    people: list[Person]

    __tablename__ = 'vehicle'
    id = db.Column(db.BIGINT(), nullable=False, primary_key=True)
    collision_id = db.Column(db.BIGINT(), db.ForeignKey('collision.id'), nullable=False)
    state_registration = db.Column(db.VARCHAR())
    type = db.Column(db.VARCHAR())
    make = db.Column(db.VARCHAR())
    model = db.Column(db.VARCHAR())
    year = db.Column(db.INTEGER())
    travel_direction = db.Column(db.VARCHAR())
    occupants = db.Column(db.INTEGER())
    driver_sex = db.Column(db.VARCHAR())
    driver_license_status = db.Column(db.VARCHAR())
    driver_license_jurisdiction = db.Column(db.VARCHAR())
    pre_crash = db.Column(db.VARCHAR())
    point_of_impact = db.Column(db.VARCHAR())
    damages = db.Column(db.ARRAY(db.VARCHAR(), as_tuple=True))
    public_property_damage = db.Column(db.VARCHAR())
    public_property_damage_type = db.Column(db.VARCHAR())
    contributing_factors = db.Column(db.ARRAY(db.VARCHAR(), as_tuple=True))
    people = db.relationship('Person', backref='vehicle', lazy='joined', viewonly=True)


@dataclass
class Collision(db.Model):
    id: int
    date: date
    time: time
    latitude: Optional[float]
    longitude: Optional[float]
    h3_index: Optional[int]
    nta2020_id: Optional[str]
    vehicles: list[Vehicle]
    people: list[Person]

    __tablename__ = 'collision'
    id = db.Column(db.BIGINT(), nullable=False, primary_key=True)
    date = db.Column(db.DATE(), nullable=False)
    time = db.Column(db.TIME(0), nullable=False)
    latitude = db.Column(db.REAL())
    longitude = db.Column(db.REAL())
    h3_index = db.Column(db.BIGINT(), db.ForeignKey('h3.h3_index'))
    nta2020_id = db.Column(db.VARCHAR(6), db.ForeignKey('nta2020.id'))
    vehicles = db.relationship('Vehicle', backref='collision', lazy=True)
    people = db.relationship('Person', backref='collision', lazy='joined', viewonly=True,
                             primaryjoin='and_(Collision.id==Person.collision_id,Person.vehicle_id==None)')
