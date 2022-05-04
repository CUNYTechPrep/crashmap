from dataclasses import asdict, is_dataclass
from datetime import date, time
from flask.json import JSONEncoder
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from h3 import h3_to_string, k_ring, string_to_h3
from sqlalchemy import sql
from typing import Any, Optional

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
    def get_collision(id: Optional[int]) -> list[Collision]:
        query = Collision.query
        if id is not None:
            query = query.filter(Collision.id == id)
        return query.all()


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
    def get_h3(h3_index: Optional[int], k: Optional[int],
               nta2020_id: Optional[str], boro_id: Optional[int], only_water: Optional[bool]) \
            -> list[H3]:
        query = H3.query
        if h3_index is not None:
            if k is None or k == 0:
                query = query.filter(H3.h3_index == h3_index)
            else:
                if k < 0 or k > 6:  # 1 cell at resolution 9 is 0.1 km². k == 6 results in a set of 127 cells—13.5 km².
                    raise ValueError('k must be a non-negative integer less than 7.')
                query = query.filter(H3.h3_index.in_(map(string_to_h3, k_ring(h3_to_string(h3_index), k))))
        elif k is not None:
            raise ValueError('k cannot be specified without h3_index.')
        if nta2020_id is not None:
            query = query.filter(H3.nta2020s.any(id=nta2020_id))
        if boro_id is not None:
            query = query.filter(H3.nta2020s.any(boro_id=boro_id))
        if only_water is not None:
            query = query.filter(H3.only_water == only_water)
        return query.all()


class NTA2020Service:
    @staticmethod
    def get_nta2020(id: Optional[str], boro_id: Optional[int]) -> list[NTA2020]:
        query = NTA2020.query
        if id is not None:
            query = query.filter(NTA2020.id == id)
        if boro_id is not None:
            query = query.filter(NTA2020.boro_id == boro_id)
        return query.all()


class SummaryService:
    SQL_TEMPLATE = '''SELECT {key_column_canceller}{key_column},
                             min(collision.date) AS start_date,
                             max(collision.date) AS end_date,
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
                             count(person.id) FILTER (WHERE person.injury = 'Killed' AND person.type = 'Other Motorized') AS others_killed
                      FROM collision
                      {additional_join}
                      LEFT JOIN vehicle ON collision.id = vehicle.collision_id
                      LEFT JOIN person ON collision.id = person.collision_id
                      WHERE collision.date BETWEEN :start_date AND :end_date {key_column_canceller}AND {key_column} = :x
                      {key_column_canceller}GROUP BY {key_column}
                      {key_column_canceller}ORDER BY {key_column}'''

    @staticmethod
    def get_summary(h3_index: Optional[int], nta2020_id: Optional[str], boro_id: Optional[int],
                    start_date: Optional[date], end_date: Optional[date]) \
            -> list[dict[str, Any]]:
        if h3_index is not None and nta2020_id is not None or \
           h3_index is not None and boro_id is not None or \
           nta2020_id is not None and boro_id is not None:
            raise ValueError('h3_index, nta2020_id, and boro_id are mutually exclusive arguments.')
        sql_customizations = {'key_column_canceller': '--',
                              'key_column': '',
                              'additional_join': '--'}
        parameters = {'start_date': '0001-01-01',
                      'end_date': '9999-12-31',
                      'x': ''}
        if h3_index is not None:
            sql_customizations['key_column_canceller'] = ''
            sql_customizations['key_column'] = 'collision.h3_index'
            parameters['x'] = h3_index
        elif nta2020_id is not None:
            sql_customizations['key_column_canceller'] = ''
            sql_customizations['key_column'] = 'collision.nta2020_id'
            parameters['x'] = nta2020_id
        elif boro_id is not None:
            sql_customizations['key_column_canceller'] = ''
            sql_customizations['key_column'] = 'nta2020.boro_id'
            sql_customizations['additional_join'] = 'INNER JOIN nta2020 ON collision.nta2020_id = nta2020.id'
            parameters['x'] = boro_id
        if start_date is not None:
            parameters['start_date'] = start_date
        if end_date is not None:
            parameters['end_date'] = end_date
        statement = sql.text(SummaryService.SQL_TEMPLATE.format(**sql_customizations))
        return [*map(dict, db.session.execute(statement, parameters))]
