from dataclasses import asdict, is_dataclass
from datetime import date, time
from flask.json import JSONEncoder
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from h3 import h3_to_string, k_ring, string_to_h3
from typing import Any, Optional, Sequence

from models import Boro, Collision, db, H3, NTA2020


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
        if id is not None:
            query = query.filter(Collision.id == id)
        if h3_index is not None:
            if k is None or k == 0:
                query = query.filter(Collision.h3_index == h3_index)
            else:
                query = query.filter(Collision.h3_index.in_(map(string_to_h3, k_ring(h3_to_string(h3_index), k))))
        elif k is not None:
            raise ValueError('k cannot be specified without h3_index.')
        if nta2020_id is not None:
            query = query.filter(Collision.nta2020_id.like(nta2020_id))
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
        if h3_index is not None:
            if k is None or k == 0:
                query = query.filter(H3.h3_index == h3_index)
            else:
                query = query.filter(H3.h3_index.in_(map(string_to_h3, k_ring(h3_to_string(h3_index), k))))
        elif k is not None:
            raise ValueError('k cannot be specified without h3_index.')
        if nta2020_id is not None:
            query = query.filter(H3.nta2020s.any(NTA2020.id.like(nta2020_id)))
        if only_water is not None:
            query = query.filter(H3.only_water == only_water)
        return query.all()


class NTA2020Service:
    @staticmethod
    def get_nta2020(id: Optional[str], boro_id: Optional[int]) -> list[NTA2020]:
        query = NTA2020.query
        if id is not None:
            query = query.filter(NTA2020.id.like(id))
        if boro_id is not None:
            query = query.filter(NTA2020.boro_id == boro_id)
        return query.all()


class SummaryService:
    COMMON_COLUMNS = '''least(min(collision.date), greatest(:start_date, (SELECT min(collision.date) FROM collision))) AS start_date,
                        greatest(max(collision.date), least(:end_date, (SELECT max(collision.date) FROM collision))) AS end_date,
                        count(DISTINCT collision.id) AS collisions,
                        count(DISTINCT vehicle.id) AS vehicles,
                        count(person.id) AS people,
                        count(person.id) FILTER (WHERE person.type = 'Occupant') AS occupants,
                        count(person.id) FILTER (WHERE person.type = 'Bicyclist') AS cyclists,
                        count(person.id) FILTER (WHERE person.type = 'Pedestrian') AS pedestrians,
                        count(person.id) FILTER (WHERE person.type = 'Other Motorized') AS others,
                        count(person.id) FILTER (WHERE person.injury = 'Injured') AS people_injured,
                        count(person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Occupant') AS occupants_injured,
                        count(person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Bicyclist') AS cyclists_injured,
                        count(person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Pedestrian') AS pedestrians_injured,
                        count(person.id) FILTER (WHERE person.injury = 'Injured' AND person.type = 'Other Motorized') AS others_injured,
                        count(person.id) FILTER (WHERE person.injury = 'Killed') AS people_killed,
                        count(person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Occupant') AS occupants_killed,
                        count(person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Bicyclist') AS cyclists_killed,
                        count(person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Pedestrian') AS pedestrians_killed,
                        count(person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Other Motorized') AS others_killed'''

    @staticmethod
    def get_h3_summary(h3_index: Optional[int], nta2020_id: Optional[str],
                       start_date: Optional[date], end_date: Optional[date]) -> list[dict[str, Any]]:
        if h3_index is not None:
            key_column = 'collision.h3_index'
            predicate = '='
            key = h3_index
        elif nta2020_id is not None:
            key_column = 'collision.nta2020_id'
            predicate = 'LIkE'
            key = nta2020_id
        else:
            raise ValueError('Invalid combination of parameters provided.')
        sql_statement = f'''SELECT collision.h3_index,
                                   {SummaryService.COMMON_COLUMNS},
                                   json_object_agg(DISTINCT collision.id, ARRAY [collision.longitude, collision.latitude]) AS collision_locations
                            FROM collision
                            LEFT JOIN vehicle ON collision.id = vehicle.collision_id
                            LEFT JOIN person ON collision.id = person.collision_id
                            WHERE {key_column} {predicate} :key
                                  (:start_date IS NULL OR :start_date <= collision.date) AND
                                  (:end_date IS NULL OR collision.date <= :end_date)
                            GROUP BY collision.h3_index
                            ORDER BY collision.h3_index'''
        parameters = {'key': key,
                      'start_date': start_date,
                      'end_date': end_date}
        return [*map(dict, db.session.execute(sql_statement, parameters))]

    @staticmethod
    def get_nta2020_summary(nta2020_id: Optional[str], boro_id: Optional[int],
                            start_date: Optional[date], end_date: Optional[date]) -> list[dict[str, Any]]:
        if nta2020_id is not None:
            key_column = 'collision.nta2020_id'
            predicate = 'LIKE'
            key = nta2020_id
        elif boro_id is not None:
            key_column = 'nta2020.boro_id'
            predicate = '='
            key = boro_id
        else:
            raise ValueError('Invalid combination of parameters provided.')
        sql_statement = f'''SELECT collision.nta2020_id,
                                   {SummaryService.COMMON_COLUMNS}
                            FROM collision
                            INNER JOIN nta2020 ON nta2020.id = collision.nta2020_id
                            LEFT JOIN vehicle ON collision.id = vehicle.collision_id
                            LEFT JOIN person ON collision.id = person.collision_id
                            WHERE {key_column} {predicate} :key
                                  (:start_date IS NULL OR :start_date <= collision.date) AND
                                  (:end_date IS NULL OR collision.date <= :end_date)
                            GROUP BY collision.nta2020_id
                            ORDER BY collision.nta2020_id'''
        parameters = {'key': key,
                      'start_date': start_date,
                      'end_date': end_date}
        return [*map(dict, db.session.execute(sql_statement, parameters))]

    @staticmethod
    def get_boro_summary(boro_id: Optional[int], start_date: Optional[date], end_date: Optional[date]) \
            -> list[dict[str, Any]]:
        if boro_id is None:
            predicate = ''
        else:
            predicate = 'nta2020.boro_id = :boro_id AND'
        sql_statement = f'''SELECT nta2020.boro_id,
                                   {SummaryService.COMMON_COLUMNS}
                            FROM collision
                            INNER JOIN nta2020 ON nta2020.id = collision.nta2020_id
                            LEFT JOIN vehicle ON collision.id = vehicle.collision_id
                            LEFT JOIN person ON collision.id = person.collision_id
                            WHERE {predicate}
                                  (:start_date IS NULL OR :start_date <= collision.date) AND
                                  (:end_date IS NULL OR collision.date <= :end_date)
                            GROUP BY nta2020.boro_id
                            ORDER BY nta2020.boro_id'''
        parameters = {'boro_id': boro_id,
                      'start_date': start_date,
                      'end_date': end_date}
        return [*map(dict, db.session.execute(sql_statement, parameters))]

    @staticmethod
    def get_city_summary(start_date: Optional[date], end_date: Optional[date]) -> list[dict[str, Any]]:
        sql_statement = f'''SELECT {SummaryService.COMMON_COLUMNS}
                            FROM collision
                            LEFT JOIN vehicle ON collision.id = vehicle.collision_id
                            LEFT JOIN person ON collision.id = person.collision_id
                            WHERE (:start_date IS NULL OR :start_date <= collision.date) AND
                                  (:end_date IS NULL OR collision.date <= :end_date)'''
        parameters = {'start_date': start_date,
                      'end_date': end_date}
        return [*map(dict, db.session.execute(sql_statement, parameters))]
