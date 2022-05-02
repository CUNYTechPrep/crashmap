from dataclasses import asdict, is_dataclass
from datetime import date, time
from flask.json import JSONEncoder
from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape


class CustomEncoder(JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        elif isinstance(o, (date, time)):
            return o.isoformat()
        elif isinstance(o, WKBElement):
            return to_shape(o).__geo_interface__
        return super().default(o)
