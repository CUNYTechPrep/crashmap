from dataclasses import dataclass
from datetime import date, time
from flask_sqlalchemy import SQLAlchemy
import geoalchemy2 as ga2
from geoalchemy2 import WKBElement
from typing import Optional

db = SQLAlchemy()

cardinal_direction = db.Enum('North', 'East', 'South', 'West', 'Northeast', 'Southeast', 'Northwest', 'Southwest',
                             name='cardinal_direction')

injury_type = db.Enum('Injured', 'Killed', name='injury_type')

person_sex = db.Enum('Female', 'Male', name='person_sex')

person_type = db.Enum('Bicyclist', 'Occupant', 'Pedestrian', 'Other Motorized', name='person_type')

us_state = db.Enum('AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                   'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD',
                   'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH',
                   'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                   'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI', 'WV', 'WY',
                   name='us_state')

h3_nta2020 = db.Table('h3_nta2020',
                      db.Column('h3_index', db.BIGINT(), db.ForeignKey('h3.h3_index')),
                      db.Column('nta2020_id', db.VARCHAR(6), db.ForeignKey('nta2020.id')))


@dataclass
class Boro(db.Model):
    id: int
    name: str
    geometry: WKBElement
    land_geometry: WKBElement

    __tablename__ = 'boro'
    id = db.Column(db.INTEGER(), nullable=False, primary_key=True)
    name = db.Column(db.VARCHAR(), nullable=False)
    geometry = ga2.Column(ga2.Geometry(), nullable=False)
    land_geometry = ga2.Column(ga2.Geometry(), nullable=False)
    # nta2020s = db.relationship('NTA2020', backref='boro', lazy=True)


@dataclass
class NTA2020(db.Model):
    id: int
    name: Optional[str]
    boro_id: int
    geometry: WKBElement

    __tablename__ = 'nta2020'
    id = db.Column(db.VARCHAR(6), nullable=False, primary_key=True)
    name = db.Column(db.VARCHAR(), unique=True)
    boro_id = db.Column(db.INTEGER(), db.ForeignKey('boro.id'), nullable=False)
    geometry = ga2.Column(ga2.Geometry())
    h3s = db.relationship('H3', secondary=h3_nta2020, backref=db.backref('h3'), viewonly=True)


@dataclass
class H3(db.Model):
    h3_index: int
    only_water: bool
    geometry: WKBElement

    __tablename__ = 'h3'
    h3_index = db.Column(db.BIGINT, nullable=False, primary_key=True)
    only_water = db.Column(db.BOOLEAN(), nullable=False)
    geometry = ga2.Column(ga2.Geometry('POLYGON'), nullable=False)
    nta2020s = db.relationship('NTA2020', secondary=h3_nta2020, backref=db.backref('nta2020'), viewonly=True)


@dataclass
class Person(db.Model):
    id: int
    collision_id: int
    vehicle_id: Optional[int]
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
    contributing_factors: list[str]
    sex: Optional[str]

    __tablename__ = 'person'
    id = db.Column(db.BIGINT(), nullable=False, primary_key=True)
    collision_id = db.Column(db.BIGINT(), db.ForeignKey('collision.id'), nullable=False)
    vehicle_id = db.Column(db.BIGINT(), db.ForeignKey('vehicle.id'))
    type = db.Column(person_type)
    injury = db.Column(injury_type)
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
    contributing_factors = db.Column(db.ARRAY(db.VARCHAR()))
    sex = db.Column(person_sex)


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
    damages: list[str]
    public_property_damage: Optional[str]
    public_property_damage_type: Optional[str]
    contributing_factors: list[str]
    people: list[Person]

    __tablename__ = 'vehicle'
    id = db.Column(db.BIGINT(), nullable=False, primary_key=True)
    collision_id = db.Column(db.BIGINT(), db.ForeignKey('collision.id'), nullable=False)
    state_registration = db.Column(us_state)
    type = db.Column(db.VARCHAR())
    make = db.Column(db.VARCHAR())
    model = db.Column(db.VARCHAR())
    year = db.Column(db.INTEGER())
    travel_direction = db.Column(cardinal_direction)
    occupants = db.Column(db.INTEGER())
    driver_sex = db.Column(db.VARCHAR())
    driver_license_status = db.Column(db.VARCHAR())
    driver_license_jurisdiction = db.Column(us_state)
    pre_crash = db.Column(db.VARCHAR())
    point_of_impact = db.Column(db.VARCHAR())
    damages = db.Column(db.ARRAY(db.VARCHAR()))
    public_property_damage = db.Column(db.VARCHAR())
    public_property_damage_type = db.Column(db.VARCHAR())
    contributing_factors = db.Column(db.ARRAY(db.VARCHAR()))
    people = db.relationship('Person', backref='vehicle', lazy=True)


@dataclass
class Collision(db.Model):
    id: int
    date: date
    time: time
    location: Optional[WKBElement]
    h3_index: Optional[int]
    nta2020_id: Optional[str]
    vehicles: list[Vehicle]
    people: list[Person]

    __tablename__ = 'collision'
    id = db.Column(db.BIGINT(), nullable=False, primary_key=True)
    date = db.Column(db.DATE(), nullable=False)
    time = db.Column(db.TIME(0), nullable=False)
    location = db.Column(ga2.Geometry('POINT'), nullable=False)
    h3_index = db.Column(db.BIGINT(), db.ForeignKey('h3.h3_index'), nullable=False)
    nta2020_id = db.Column(db.VARCHAR(6), db.ForeignKey('nta2020.id'), nullable=False)
    vehicles = db.relationship('Vehicle', backref='collision', lazy=True)
    people = db.relationship('Person', backref='collision',
                             primaryjoin='and_(Collision.id==Person.collision_id,Person.vehicle_id==None)', lazy=True)


@dataclass
class CitySummary(db.Model):
    date: date
    collisions: int
    vehicles: int
    people: int
    occupants: int
    cyclists: int
    pedestrians: int
    other_people: int
    people_injured: int
    occupants_injured: int
    cyclists_injured: int
    pedestrians_injured: int
    other_people_injured: int
    people_killed: int
    occupants_killed: int
    cyclists_killed: int
    pedestrians_killed: int
    other_people_killed: int

    __tablename__ = 'city_summary'
    date = db.Column(db.DATE(), nullable=False, primary_key=True)
    collisions = db.Column(db.BIGINT(), db.CheckConstraint('collisions >= 0)'), nullable=False)
    vehicles = db.Column(db.BIGINT(), db.CheckConstraint('vehicles >= 0)'), nullable=False)
    people = db.Column(db.BIGINT(), db.CheckConstraint('people >= 0)'), nullable=False)
    occupants = db.Column(db.BIGINT(), db.CheckConstraint('occupants >= 0)'), nullable=False)
    cyclists = db.Column(db.BIGINT(), db.CheckConstraint('cyclists >= 0)'), nullable=False)
    pedestrians = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians >= 0)'), nullable=False)
    other_people = db.Column(db.BIGINT(), db.CheckConstraint('other_people >= 0)'), nullable=False)
    people_injured = db.Column(db.BIGINT(), db.CheckConstraint('people_injured >= 0)'), nullable=False)
    occupants_injured = db.Column(db.BIGINT(), db.CheckConstraint('occupants_injured >= 0)'), nullable=False)
    cyclists_injured = db.Column(db.BIGINT(), db.CheckConstraint('cyclists_injured >= 0)'), nullable=False)
    pedestrians_injured = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians_injured >= 0)'), nullable=False)
    other_people_injured = db.Column(db.BIGINT(), db.CheckConstraint('other_people_injured >= 0)'), nullable=False)
    people_killed = db.Column(db.BIGINT(), db.CheckConstraint('people_killed >= 0)'), nullable=False)
    occupants_killed = db.Column(db.BIGINT(), db.CheckConstraint('occupants_killed >= 0)'), nullable=False)
    cyclists_killed = db.Column(db.BIGINT(), db.CheckConstraint('cyclists_killed >= 0)'), nullable=False)
    pedestrians_killed = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians_killed >= 0)'), nullable=False)
    other_people_killed = db.Column(db.BIGINT(), db.CheckConstraint('other_people_killed >= 0)'), nullable=False)


@dataclass
class BoroSummary(db.Model):
    boro_id: int
    date: date
    collisions: int
    vehicles: int
    people: int
    occupants: int
    cyclists: int
    pedestrians: int
    other_people: int
    people_injured: int
    occupants_injured: int
    cyclists_injured: int
    pedestrians_injured: int
    other_people_injured: int
    people_killed: int
    occupants_killed: int
    cyclists_killed: int
    pedestrians_killed: int
    other_people_killed: int

    __tablename__ = 'boro_summary'
    boro_id = db.Column(db.BIGINT(), db.ForeignKey('boro_id'), nullable=False, primary_key=True)
    date = db.Column(db.DATE(), nullable=False, primary_key=True)
    collisions = db.Column(db.BIGINT(), db.CheckConstraint('collisions >= 0)'), nullable=False)
    vehicles = db.Column(db.BIGINT(), db.CheckConstraint('vehicles >= 0)'), nullable=False)
    people = db.Column(db.BIGINT(), db.CheckConstraint('people >= 0)'), nullable=False)
    occupants = db.Column(db.BIGINT(), db.CheckConstraint('occupants >= 0)'), nullable=False)
    cyclists = db.Column(db.BIGINT(), db.CheckConstraint('cyclists >= 0)'), nullable=False)
    pedestrians = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians >= 0)'), nullable=False)
    other_people = db.Column(db.BIGINT(), db.CheckConstraint('other_people >= 0)'), nullable=False)
    people_injured = db.Column(db.BIGINT(), db.CheckConstraint('people_injured >= 0)'), nullable=False)
    occupants_injured = db.Column(db.BIGINT(), db.CheckConstraint('occupants_injured >= 0)'), nullable=False)
    cyclists_injured = db.Column(db.BIGINT(), db.CheckConstraint('cyclists_injured >= 0)'), nullable=False)
    pedestrians_injured = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians_injured >= 0)'), nullable=False)
    other_people_injured = db.Column(db.BIGINT(), db.CheckConstraint('other_people_injured >= 0)'), nullable=False)
    people_killed = db.Column(db.BIGINT(), db.CheckConstraint('people_killed >= 0)'), nullable=False)
    occupants_killed = db.Column(db.BIGINT(), db.CheckConstraint('occupants_killed >= 0)'), nullable=False)
    cyclists_killed = db.Column(db.BIGINT(), db.CheckConstraint('cyclists_killed >= 0)'), nullable=False)
    pedestrians_killed = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians_killed >= 0)'), nullable=False)
    other_people_killed = db.Column(db.BIGINT(), db.CheckConstraint('other_people_killed >= 0)'), nullable=False)
    __tableargs__ = (db.PrimaryKeyConstraint(boro_id, date),)


@dataclass
class NTA2020Summary(db.Model):
    nta2020_id: str
    date: date
    collisions: int
    vehicles: int
    people: int
    occupants: int
    cyclists: int
    pedestrians: int
    other_people: int
    people_injured: int
    occupants_injured: int
    cyclists_injured: int
    pedestrians_injured: int
    other_people_injured: int
    people_killed: int
    occupants_killed: int
    cyclists_killed: int
    pedestrians_killed: int
    other_people_killed: int

    __tablename__ = 'nta2020_summary'
    nta2020_id = db.Column(db.VARCHAR(6), db.ForeignKey('nta2020.id'), nullable=False, primary_key=True)
    date = db.Column(db.DATE(), nullable=False, primary_key=True)
    collisions = db.Column(db.BIGINT(), db.CheckConstraint('collisions >= 0)'), nullable=False)
    vehicles = db.Column(db.BIGINT(), db.CheckConstraint('vehicles >= 0)'), nullable=False)
    people = db.Column(db.BIGINT(), db.CheckConstraint('people >= 0)'), nullable=False)
    occupants = db.Column(db.BIGINT(), db.CheckConstraint('occupants >= 0)'), nullable=False)
    cyclists = db.Column(db.BIGINT(), db.CheckConstraint('cyclists >= 0)'), nullable=False)
    pedestrians = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians >= 0)'), nullable=False)
    other_people = db.Column(db.BIGINT(), db.CheckConstraint('other_people >= 0)'), nullable=False)
    people_injured = db.Column(db.BIGINT(), db.CheckConstraint('people_injured >= 0)'), nullable=False)
    occupants_injured = db.Column(db.BIGINT(), db.CheckConstraint('occupants_injured >= 0)'), nullable=False)
    cyclists_injured = db.Column(db.BIGINT(), db.CheckConstraint('cyclists_injured >= 0)'), nullable=False)
    pedestrians_injured = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians_injured >= 0)'), nullable=False)
    other_people_injured = db.Column(db.BIGINT(), db.CheckConstraint('other_people_injured >= 0)'), nullable=False)
    people_killed = db.Column(db.BIGINT(), db.CheckConstraint('people_killed >= 0)'), nullable=False)
    occupants_killed = db.Column(db.BIGINT(), db.CheckConstraint('occupants_killed >= 0)'), nullable=False)
    cyclists_killed = db.Column(db.BIGINT(), db.CheckConstraint('cyclists_killed >= 0)'), nullable=False)
    pedestrians_killed = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians_killed >= 0)'), nullable=False)
    other_people_killed = db.Column(db.BIGINT(), db.CheckConstraint('other_people_killed >= 0)'), nullable=False)
    __tableargs__ = (db.PrimaryKeyConstraint(nta2020_id, date),)


@dataclass
class H3Summary(db.Model):
    h3_index: int
    date: date
    collisions: int
    vehicles: int
    people: int
    occupants: int
    cyclists: int
    pedestrians: int
    other_people: int
    people_injured: int
    occupants_injured: int
    cyclists_injured: int
    pedestrians_injured: int
    other_people_injured: int
    people_killed: int
    occupants_killed: int
    cyclists_killed: int
    pedestrians_killed: int
    other_people_killed: int

    __tablename__ = 'h3_summary'
    h3_index = db.Column(db.BIGINT(), db.ForeignKey('h3.h3_index'), nullable=False, primary_key=True)
    date = db.Column(db.DATE(), nullable=False, primary_key=True)
    collisions = db.Column(db.BIGINT(), db.CheckConstraint('collisions >= 0)'), nullable=False)
    vehicles = db.Column(db.BIGINT(), db.CheckConstraint('vehicles >= 0)'), nullable=False)
    people = db.Column(db.BIGINT(), db.CheckConstraint('people >= 0)'), nullable=False)
    occupants = db.Column(db.BIGINT(), db.CheckConstraint('occupants >= 0)'), nullable=False)
    cyclists = db.Column(db.BIGINT(), db.CheckConstraint('cyclists >= 0)'), nullable=False)
    pedestrians = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians >= 0)'), nullable=False)
    other_people = db.Column(db.BIGINT(), db.CheckConstraint('other_people >= 0)'), nullable=False)
    people_injured = db.Column(db.BIGINT(), db.CheckConstraint('people_injured >= 0)'), nullable=False)
    occupants_injured = db.Column(db.BIGINT(), db.CheckConstraint('occupants_injured >= 0)'), nullable=False)
    cyclists_injured = db.Column(db.BIGINT(), db.CheckConstraint('cyclists_injured >= 0)'), nullable=False)
    pedestrians_injured = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians_injured >= 0)'), nullable=False)
    other_people_injured = db.Column(db.BIGINT(), db.CheckConstraint('other_people_injured >= 0)'), nullable=False)
    people_killed = db.Column(db.BIGINT(), db.CheckConstraint('people_killed >= 0)'), nullable=False)
    occupants_killed = db.Column(db.BIGINT(), db.CheckConstraint('occupants_killed >= 0)'), nullable=False)
    cyclists_killed = db.Column(db.BIGINT(), db.CheckConstraint('cyclists_killed >= 0)'), nullable=False)
    pedestrians_killed = db.Column(db.BIGINT(), db.CheckConstraint('pedestrians_killed >= 0)'), nullable=False)
    other_people_killed = db.Column(db.BIGINT(), db.CheckConstraint('other_people_killed >= 0)'), nullable=False)
    __tableargs__ = (db.PrimaryKeyConstraint(h3_index, date),)
