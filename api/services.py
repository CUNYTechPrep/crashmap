from dataclasses import asdict, is_dataclass
from datetime import date, time
from flask.json import JSONEncoder
from functools import partial, reduce
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from h3 import h3_to_string, k_ring, string_to_h3
from itertools import chain
from operator import is_not
from sqlalchemy import func, select
import sqlalchemy.dialects.postgresql as postgresql
from typing import Any, Iterable, Optional, Sequence

from models import Boro, Collision, db, H3, NTA2020, Person, Vehicle


class BoroService:
    @staticmethod
    def get_boro(id: Optional[int]) -> list[Boro]:
        query = Boro.query
        if id is not None:
            query = query.filter(Boro.id == id)
        return query.all()


class CollisionService:
    @staticmethod
    def get_collision(id: Optional[int], h3_index: Optional[int], k: Optional[int], nta2020_id: Optional[str],
                      start_date: Optional[date], end_date: Optional[date]) -> list[Collision]:
        query = Collision.query
        match (id, h3_index, k, nta2020_id):
            case (None, None, None, None):
                pass
            case (id, None, None, None):
                query = query.filter(Collision.id == id)
            case (None, h3_index, k, None) if k is None or k >= 0:
                if k:
                    query = query.filter(Collision.h3_index.in_(map(string_to_h3, k_ring(h3_to_string(h3_index), k))))
                else:
                    query = query.filter(Collision.h3_index == h3_index)
            case (None, None, None, nta2020_id):
                query = query.filter(Collision.nta2020_id.like(nta2020_id))
            case _:
                raise ValueError('Invalid combination of arguments provided.')
        if start_date is not None:
            query = query.filter(start_date <= Collision.date)
        if end_date is not None:
            query = query.filter(Collision.date <= end_date)
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


class H3Service:
    @staticmethod
    def get_h3(h3_index: Optional[int], k: Optional[int], nta2020_id: Optional[str], only_water: Optional[bool]) \
            -> list[H3]:
        query = H3.query
        match (h3_index, k, nta2020_id):
            case (None, None, None):
                pass
            case (h3_index, k, None) if k is None or k >= 0:
                if k:
                    query = query.filter(H3.h3_index.in_(map(string_to_h3, k_ring(h3_to_string(h3_index), k))))
                else:
                    query = query.filter(H3.h3_index == h3_index)
            case (None, None, nta2020_id):
                query = query.filter(H3.nta2020s.any(NTA2020.id.like(nta2020_id)))
        if only_water is not None:
            query = query.filter(H3.only_water == only_water)
        return query.all()


class NTA2020Service:
    @staticmethod
    def get_nta2020(id: Optional[str], boro_id: Optional[int]) -> list[NTA2020]:
        query = NTA2020.query
        match (id, boro_id):
            case (None, None):
                pass
            case (id, None):
                query = query.filter(NTA2020.id.like(id))
            case (None, boro_id):
                query = query.filter(NTA2020.boro_id == boro_id)
            case _:
                raise ValueError('Invalid combination of arguments provided.')
        return query.all()


class SummaryService:
    @staticmethod
    def get_summary(start_date: Optional[date], end_date: Optional[date], predicate: Optional[Any] = None,
                    distinct_columns: Iterable = (), additional_columns: Iterable = (),
                    join_model: Optional[db.Model] = None, join_clause: Optional[Any] = None) -> list[dict[str, Any]]:
        query = Collision.query
        if join_model or join_clause:
            query = query.join(join_model, join_clause)
        query = query.join(Vehicle, Collision.id == Vehicle.collision_id, isouter=True) \
                     .join(Person, Collision.id == Person.collision_id, isouter=True) \
                     .where(Collision.longitude.is_not(None)) \
                     .where(Collision.latitude.is_not(None))
        if predicate is not None:
            query = query.where(predicate)
        if start_date:
            query = query.where(start_date <= Collision.date)
        if end_date:
            query = query.where(Collision.date <= end_date)
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
    def get_h3_summary(h3_index: Optional[int], k: Optional[int], nta2020_id: Optional[str],
                       start_date: Optional[date], end_date: Optional[date]) -> list[dict[str, Any]]:
        match (h3_index, k, nta2020_id):
            case (None, None, None):
                predicate = None
            case (h3_index, k, None) if k is None or k >= 0:
                if k:
                    predicate = Collision.h3_index.in_(map(string_to_h3, k_ring(h3_to_string(h3_index), k)))
                else:
                    predicate = Collision.h3_index == h3_index
            case (None, None, nta2020_id):
                predicate = Collision.nta2020_id.like(nta2020_id)
            case _:
                raise ValueError('Invalid combination of arguments provided.')
        return SummaryService.get_summary(start_date, end_date,
                                          predicate, (Collision.h3_index,),
                                          (func.json_object_agg(Collision.id.distinct(),
                                                                postgresql.array((Collision.longitude,
                                                                                  Collision.latitude)))
                                               .label('collision_locations'),))

    @staticmethod
    def get_nta2020_summary(nta2020_id: Optional[str], boro_id: Optional[int],
                            start_date: Optional[date], end_date: Optional[date]) -> list[dict[str, Any]]:
        match (nta2020_id, boro_id):
            case (None, None):
                arguments = {}
            case (nta2020_id, None):
                arguments = {'predicate': Collision.nta2020_id.like(nta2020_id)}
            case (None, boro_id):
                arguments = {'join_model': NTA2020,
                             'join_clause': NTA2020.id == Collision.nta2020_id,
                             'predicate': NTA2020.boro_id == boro_id}
            case _:
                raise ValueError('Invalid combination of arguments provided.')
        return SummaryService.get_summary(start_date, end_date, distinct_columns=(Collision.nta2020_id,), **arguments)

    @staticmethod
    def get_boro_summary(boro_id: Optional[int], start_date: Optional[date], end_date: Optional[date]) \
            -> list[dict[str, Any]]:
        predicate = NTA2020.boro_id == boro_id \
                    if boro_id \
                    else None
        return SummaryService.get_summary(start_date, end_date, predicate, (NTA2020.boro_id,),
                                          join_model=NTA2020, join_clause=NTA2020.id == Collision.nta2020_id)
