from dataclasses import asdict, is_dataclass
from datetime import date, time
from flask.json import JSONEncoder
from flask_sqlalchemy import BaseQuery
from functools import partial, reduce
from geoalchemy2 import WKBElement
from geoalchemy2 import func as geo_func
from geoalchemy2.shape import to_shape
from h3 import h3_to_string, k_ring, string_to_h3
from itertools import chain
from operator import is_not
from sqlalchemy import and_, func, join, or_, select
from sqlalchemy.sql import Selectable
from sqlalchemy.types import JSON
import sqlalchemy.dialects.postgresql as postgresql
from typing import Any, Iterable, Optional, Sequence

from models import Boro, Collision, db, H3, h3_nta2020, NTA2020, Person, Vehicle


class GeoService:
    @staticmethod
    def get_all() -> dict:
        sql_statement = '''SELECT json_build_object('type', 'FeatureCollection',
                                                    'features', json_agg(st_asgeojson(b)::json)) AS geojson
                           FROM (SELECT boro.*,
                                        json_build_object('type', 'FeatureCollection',
                                                          'features', json_agg(st_asgeojson(n)::json)) AS nta2020s
                                 FROM (SELECT nta2020.*,
                                              json_build_object('type', 'FeatureCollection',
                                                                'features', json_agg(h.geojson)) AS h3s
                                       FROM (SELECT h3_nta2020.nta2020_id,
                                                    st_asgeojson(h3)::json AS geojson
                                             FROM h3
                                             JOIN h3_nta2020 ON h3.h3_index = h3_nta2020.h3_index) AS h
                                       JOIN nta2020 ON nta2020.id = h.nta2020_id
                                       GROUP BY nta2020.id) AS n
                                 JOIN boro ON n.boro_id = boro.id
                                 GROUP BY boro.id) AS b;'''
        return db.session.execute(sql_statement).scalar()

    @staticmethod
    def get_boro(id: Optional[int]) -> dict:
        subquery = db.session.query(Boro, func.array_agg(NTA2020.id).label('nta2020s')) \
                             .select_from(join(Boro, NTA2020))
        if id is not None:
            subquery = subquery.filter(Boro.id == id)
        subquery = subquery.group_by(Boro) \
                           .subquery()
        return GeoService.query_geojson_agg(subquery) \
                         .scalar()

    @staticmethod
    def get_nta2020(id: Optional[str], boro_id: Optional[int]) -> dict:
        subquery = db.session.query(NTA2020, func.array_agg(H3.h3_index).label('h3s')) \
                             .select_from(join(join(NTA2020, h3_nta2020), H3))
        match (id, boro_id):
            case (None, None):
                pass
            case (id, None):
                subquery = subquery.filter(NTA2020.id.like(id))
            case (None, boro_id):
                subquery = subquery.filter(NTA2020.boro_id == boro_id)
            case _:
                raise ValueError('Invalid combination of arguments provided.')
        subquery = subquery.group_by(NTA2020) \
                           .subquery()
        return GeoService.query_geojson_agg(subquery) \
                         .scalar()

    @staticmethod
    def get_h3(h3_index: Optional[int], k: Optional[int], nta2020_id: Optional[str], only_water: Optional[bool]) \
            -> dict:
        subquery = db.session.query(H3, func.array_agg(NTA2020.id).label('nta2020s')) \
                             .select_from(join(join(H3, h3_nta2020), NTA2020))
        match (h3_index, k, nta2020_id):
            case (None, None, None):
                pass
            case (h3_index, k, None) if k is None or k >= 0:
                if k:
                    subquery = subquery.filter(H3.h3_index.in_(map(string_to_h3, k_ring(h3_to_string(h3_index), k))))
                else:
                    subquery = subquery.filter(H3.h3_index == h3_index)
            case (None, None, nta2020_id):
                subquery = subquery.filter(H3.nta2020s.any(NTA2020.id.like(nta2020_id)))
        if only_water is not None:
            subquery = subquery.filter(H3.only_water == only_water)
        subquery = subquery.group_by(H3) \
                           .subquery()
        return GeoService.query_geojson_agg(subquery) \
                         .scalar()

    @staticmethod
    def query_geojson_agg(query: Selectable) -> BaseQuery:
        return db.session.query(func.json_build_object('type',
                                                       'FeatureCollection',
                                                       'features',
                                                       func.json_agg(geo_func.ST_AsGeoJSON(query).cast(JSON))
                                                           .label('feature')))


class CollisionService:
    @staticmethod
    def get_collision(id: Optional[int], h3_index: Optional[int], k: Optional[int], nta2020_id: Optional[str],
                      rectangle: Optional[tuple[tuple[float, float], tuple[float, float]]],
                      start_date: Optional[date], end_date: Optional[date],
                      start_time: Optional[time], end_time: Optional[time]) -> list[Collision]:
        query = Collision.query
        match (id, h3_index, k, nta2020_id, rectangle):
            case (None, None, None, None, None):
                query = query.filter(and_(Collision.latitude.is_not(None), Collision.longitude.is_not(None)))
            case (id, None, None, None, None):
                query = query.filter(Collision.id == id)
            case (None, h3_index, k, None, None) if k is None or k >= 0:
                if k:
                    query = query.filter(Collision.h3_index.in_(map(string_to_h3, k_ring(h3_to_string(h3_index), k))))
                else:
                    query = query.filter(Collision.h3_index == h3_index)
            case (None, None, None, nta2020_id, None):
                query = query.filter(Collision.nta2020_id.like(nta2020_id))
            case (None, None, None, None, rectangle):
                query = query.filter(geo_func.ST_Contains(geo_func.ST_MakeEnvelope(*chain.from_iterable(rectangle)),
                                                          geo_func.ST_Point(Collision.longitude, Collision.latitude)))
            case _:
                raise ValueError('Invalid combination of arguments provided.')
        if start_date is not None:
            query = query.filter(start_date <= Collision.date)
        if end_date is not None:
            query = query.filter(Collision.date <= end_date)
        match (start_time, end_time):
            case (None, None):
                pass
            case (start_time, None):
                query = query.filter(start_time <= Collision.time)
            case (None, end_time):
                query = query.filter(Collision.time <= end_time)
            case (start_time, end_time) if start_time < end_time:
                query = query.filter(and_(start_time <= Collision.time, Collision.time <= end_time))
            case (start_time, end_time) if start_time > end_time:
                query = query.filter(or_(start_time <= Collision.time, Collision.time <= end_time))
            case _:  # start_time == end_time
                query = query.filter(Collision.time == start_time)
        return query.all()

    @staticmethod
    def get_collisions(ids: Sequence) -> list[Collision]:
        return Collision.query.filter(Collision.id.in_(ids)).all()


class CustomEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if is_dataclass(o):
            return asdict(o)
        elif isinstance(o, (date, time)):
            return o.isoformat()
        elif isinstance(o, WKBElement):
            return to_shape(o).__geo_interface__
        return super().default(o)


class SummaryService:
    @staticmethod
    def get_summary(start_date: Optional[date] = None, end_date: Optional[date] = None,
                    start_time: Optional[time] = None, end_time: Optional[time] = None,
                    predicate: Optional[Any] = None, distinct_columns: Iterable = (), additional_columns: Iterable = (),
                    join_model: Optional[db.Model] = None, join_clause: Optional[Any] = None) -> list[dict[str, Any]]:
        query = Collision.query
        if join_model is not None or join_clause is not None:
            query = query.join(join_model, join_clause)
        query = query.join(Vehicle, Collision.id == Vehicle.collision_id, isouter=True) \
                     .join(Person, Collision.id == Person.collision_id, isouter=True)
        if predicate is not None:
            query = query.where(predicate)
        if start_date:
            query = query.where(start_date <= Collision.date)
        if end_date:
            query = query.where(Collision.date <= end_date)
        match (start_time, end_time):
            case (None, None):
                pass
            case (start_time, None):
                query = query.where(start_time <= Collision.time)
            case (None, end_time):
                query = query.where(Collision.time <= end_time)
            case (start_time, end_time) if start_time < end_time:
                query = query.where(and_(start_time <= Collision.time, Collision.time <= end_time))
            case (start_time, end_time) if start_time > end_time:
                query = query.where(or_(start_time <= Collision.time, Collision.time <= end_time))
            case _:  # start_time == end_time
                query = query.where(Collision.time == start_time)
        if distinct_columns:
            query = query.group_by(*distinct_columns) \
                         .order_by(*distinct_columns)
        columns = chain(distinct_columns,
                        (func.least(func.min(Collision.date),
                                    func.greatest(start_date,
                                                  select(func.min(Collision.date)).scalar_subquery()))
                             .label('start_date'),
                         func.greatest(func.max(Collision.date),
                                       func.least(end_date,
                                                  select(func.max(Collision.date)).scalar_subquery()))
                             .label('end_date'),
                         func.count(Collision.id.distinct())
                             .label('collisions'),
                         func.count(Vehicle.id.distinct())
                             .label('vehicles')),
                        chain.from_iterable((reduce(lambda _, criterion: _.filter(criterion),
                                                    filter(partial(is_not, None),
                                                           (injury_predicate, person_type_predicate)),
                                                    func.count(Person.id)).label(f'{person_type}{injury_suffix}')
                                             for person_type, person_type_predicate
                                             in (('people', None),
                                                 ('occupants', Person.type == 'Occupant'),
                                                 ('cyclists', Person.type == 'Bicyclist'),
                                                 ('pedestrians', Person.type == 'Pedestrian'),
                                                 ('others', Person.type == 'Other Motorized')))
                                            for injury_suffix, injury_predicate
                                            in (('', None),
                                                ('_injured', Person.injury == 'Injured'),
                                                ('_killed', Person.injury == 'Killed'))),
                        additional_columns)
        return [*map(dict, query.values(*columns))]

    @staticmethod
    def get_h3_summary(h3_index: Optional[int], k: Optional[int], nta2020_id: Optional[str], boro_id: Optional[int],
                       rectangle: Optional[tuple[tuple[float, float], tuple[float, float]]],
                       start_date: Optional[date], end_date: Optional[date],
                       start_time: Optional[time], end_time: Optional[time],
                       include_collision_locations: Optional[bool]) -> list[dict[str, Any]]:
        match (h3_index, k, nta2020_id, boro_id, rectangle):
            case (None, None, None, None, None):
                arguments = {'predicate': Collision.h3_index.is_not(None)}
            case (h3_index, k, None, None, None) if k is None or k >= 0:
                if k:
                    arguments = {'predicate': Collision.h3_index.in_(map(string_to_h3,
                                                                         k_ring(h3_to_string(h3_index), k)))}
                else:
                    arguments = {'predicate': Collision.h3_index == h3_index}
            case (None, None, nta2020_id, None, None):
                arguments = {'predicate': Collision.nta2020_id.like(nta2020_id)}
            case (None, None, None, boro_id, None):
                arguments = {'join_model': NTA2020,
                             'join_clause': Collision.nta2020_id == NTA2020.id,
                             'predicate': NTA2020.boro_id == boro_id}
            case (None, None, None, None, rectangle):
                arguments = {'join_model': H3,
                             'join_clause': H3.h3_index == Collision.h3_index,
                             'predicate': geo_func.ST_Intersects(geo_func.ST_MakeEnvelope(*chain(*rectangle)),
                                                                 H3.geometry)}
            case _:
                raise ValueError('Invalid combination of arguments provided.')
        additional_columns = (func.json_object_agg(Collision.id.distinct(),
                                                   postgresql.array((Collision.longitude, Collision.latitude)))
                                  .label('collision_locations'),) \
                             if include_collision_locations \
                             else ()
        return SummaryService.get_summary(start_date, end_date, start_time, end_time,
                                          distinct_columns=(Collision.h3_index,), additional_columns=additional_columns,
                                          **arguments)

    @staticmethod
    def get_nta2020_summary(nta2020_id: Optional[str], boro_id: Optional[int],
                            rectangle: Optional[tuple[tuple[float, float], tuple[float, float]]],
                            start_date: Optional[date], end_date: Optional[date],
                            start_time: Optional[time], end_time: Optional[time]) -> list[dict[str, Any]]:
        match (nta2020_id, boro_id, rectangle):
            case (None, None, None):
                arguments = {'predicate': Collision.nta2020_id.is_not(None)}
            case (nta2020_id, None, None):
                arguments = {'predicate': Collision.nta2020_id.like(nta2020_id)}
            case (None, boro_id, None):
                arguments = {'join_model': NTA2020,
                             'join_clause': NTA2020.id == Collision.nta2020_id,
                             'predicate': NTA2020.boro_id == boro_id}
            case (None, None, rectangle):
                arguments = {'join_model': NTA2020,
                             'join_clause': NTA2020.id == Collision.nta2020_id,
                             'predicate': geo_func.ST_Intersects(geo_func.ST_MakeEnvelope(*chain(*rectangle)),
                                                                 NTA2020.geometry)}
            case _:
                raise ValueError('Invalid combination of arguments provided.')
        return SummaryService.get_summary(start_date, end_date, start_time, end_time,
                                          distinct_columns=(Collision.nta2020_id,), **arguments)

    @staticmethod
    def get_boro_summary(boro_id: Optional[int], rectangle: Optional[tuple[tuple[float, float], tuple[float, float]]],
                         start_date: Optional[date], end_date: Optional[date],
                         start_time: Optional[time], end_time: Optional[time]) -> list[dict[str, Any]]:
        match (boro_id, rectangle):
            case (boro_id, None):
                arguments = {'join_model': NTA2020,
                             'join_clause': NTA2020.id == Collision.nta2020_id,
                             'predicate': NTA2020.boro_id == boro_id}
            case (None, rectangle):
                arguments = {'join_model': join(NTA2020, Boro, Boro.id == NTA2020.boro_id),
                             'join_clause': NTA2020.id == Collision.nta2020_id,
                             'predicate': geo_func.ST_Intersects(geo_func.ST_MakeEnvelope(*chain(*rectangle)),
                                                                 Boro.geometry)}
            case _:
                raise ValueError('Invalid combination of arguments provided.')
        return SummaryService.get_summary(start_date, end_date, start_time, end_time,
                                          distinct_columns=(NTA2020.boro_id,), **arguments)

    @staticmethod
    def get_city_summary(start_date: Optional[date], end_date: Optional[date],
                         start_time: Optional[time], end_time: Optional[time]) -> list[dict[str, Any]]:
        return SummaryService.get_summary(start_date, end_date, start_time, end_time, Collision.h3_index.is_not(None))
