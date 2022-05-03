from dataclasses import asdict, is_dataclass
from datetime import date, time
from flask.json import JSONEncoder
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from h3 import h3_to_string, k_ring, string_to_h3
from typing import Optional

from models import Boro, BoroSummary, CitySummary, Collision, db, H3, H3Summary, NTA2020, NTA2020Summary, Person, Vehicle


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
    def default(self, o):
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
    @staticmethod
    def get_summary(h3_index: Optional[int], nta2020_id: Optional[str], boro_id: Optional[int],
                    start_date: Optional[date], end_date: Optional[date]) \
            -> list[BoroSummary | CitySummary | H3Summary | NTA2020Summary]:
        if h3_index is not None and nta2020_id is not None or \
           h3_index is not None and boro_id is not None or \
           nta2020_id is not None and boro_id is not None:
            raise ValueError('h3_index, nta2020_id, and boro_id are mutually exclusive arguments.')
        if h3_index is not None:
            model = H3Summary
            query = model.query.filter(model.h3_index == h3_index)
        elif nta2020_id is not None:
            model = NTA2020Summary
            query = model.query.filter(model.nta2020_id == nta2020_id)
        elif boro_id is not None:
            model = BoroSummary
            query = model.query.filter(model.boro_id == boro_id)
        else:
            model = CitySummary
            query = model.query
        if start_date is not None:
            query = query.filter(model.date >= start_date)
        if end_date is not None:
            query = query.filter(model.date <= end_date)
        return query.all()
