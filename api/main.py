from ast import literal_eval
from dateutil.parser import isoparser
from math import isfinite
from os import getenv
from flask import Flask, jsonify, make_response, request, Response
from toolz import juxt, pipe
from typing import Any, Optional, Sequence

from models import db
from services import CollisionService, CustomEncoder, GeoService, SummaryService


def create_app() -> Flask:  # TODO: Move views to a separate file
    app = Flask(__name__,
                static_folder='../client/build',  # The React app is served from this local path.
                static_url_path='/')
    app.json_encoder = CustomEncoder
    db_uri = {component: getenv(f'DATABASE_{component}')
              for component in ('SCHEME', 'HOST', 'PORT', 'USERNAME', 'PASSWORD', 'NAME')}
    app.config['SQLALCHEMY_DATABASE_URI'] = '{SCHEME}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{NAME}'.format(**db_uri)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if app.debug:
        app.config['SQLALCHEMY_ECHO'] = True
        app.config['SQLALCHEMY_RECORD_QUERIES'] = True
    db.init_app(app)

    parse_isodate, parse_isotime = pipe(isoparser(),
                                        juxt(lambda _: _.parse_isodate,
                                             lambda _: _.parse_isotime))

    def bool_from_str(value: Optional[str]) -> Optional[bool]:
        match value.lower():
            case None:
                return None
            case '' | '0' | 'f' | 'false' | 'n' | 'no' | '✗':
                return False
            case '1' | 't' | 'true' | 'y' | 'yes' | '✓':
                return True
            case _:
                raise ValueError(f'{value!r} could not be converted to type bool.')

    def get_all_request_args(expected_args: dict[str, Any]) -> dict[str, Any]:
        return {key: request.args.get(key, None, parser)
                for key, parser in expected_args.items()}

    def make_geojson_response(obj: dict | list) -> Response:
        response = make_response({'type': 'FeatureCollection',
                                  'features': obj}
                                 if type(obj) is list
                                 else obj)
        response.headers['Content-type'] = 'application/geo+json'
        return response

    def parse_location_pair(value: Optional[str]) -> Optional[tuple[tuple[float, float], tuple[float, float]]]:
        if value is None:
            return None
        if len(value) >= 128:
            raise ValueError(f'The value’s length of {len(value):,} exceeds the maximum of 127.')
        match literal_eval(value):
            case result if isinstance(result, Sequence) and len(result) == 2 and \
                           all(isinstance(_, Sequence) and len(_) == 2 and all(map(isfinite, _)) for _ in result):
                return result
            case _:
                raise ValueError(f'{value!r} could not be converted to type ((float, float), (float, float)).')

    @app.route('/')
    def index() -> Response:
        return app.send_static_file('index.html')

    @app.route('/api/all.geojson', methods=['GET'])
    def all_as_geojson() -> Response:
        return make_geojson_response(GeoService.get_all())

    @app.route('/api/boro.geojson', methods=['GET'])
    def boro_as_geojson() -> Response:
        return jsonify(GeoService.get_boro(request.args.get('id', None, int)))

    @app.route('/api/nta2020.geojson', methods=['GET'])
    def nta2020_as_geojson() -> Response:
        arguments = get_all_request_args({'id': str,
                                          'boro_id': int})
        return make_geojson_response(GeoService.get_nta2020(**arguments))

    @app.route('/api/h3.geojson', methods=['GET'])
    def h3_as_geojson() -> Response:
        arguments = get_all_request_args({'h3_index': int,
                                          'k': int,
                                          'nta2020_id': str,
                                          'only_water': bool_from_str})
        return make_geojson_response(GeoService.get_h3(**arguments))

    @app.route('/api/collision.json', methods=['GET', 'POST'])
    def collision_as_geojson() -> Response:
        if request.method == 'POST':
            return jsonify(CollisionService.get_collisions(request.json))
        arguments = get_all_request_args({'id': int,
                                          'h3_index': int,
                                          'k': int,
                                          'nta2020_id': str,
                                          'rectangle': parse_location_pair,
                                          'start_date': parse_isodate,
                                          'end_date': parse_isodate,
                                          'start_time': parse_isotime,
                                          'end_time': parse_isotime})
        print(arguments)
        return jsonify(CollisionService.get_collision(**arguments))

    @app.route('/api/h3_summary.json', methods=['GET'])
    def h3_summary_as_json() -> Response:
        arguments = get_all_request_args({'h3_index': int,
                                          'k': int,
                                          'nta2020_id': str,
                                          'rectangle': parse_location_pair,
                                          'start_date': parse_isodate,
                                          'end_date': parse_isodate,
                                          'start_time': parse_isotime,
                                          'end_time': parse_isotime,
                                          'include_collision_locations': bool_from_str})
        return jsonify(SummaryService.get_h3_summary(**arguments))

    @app.route('/api/nta2020_summary.json', methods=['GET'])
    def nta2020_summary_as_json() -> Response:
        arguments = get_all_request_args({'nta2020_id': str,
                                          'boro_id': int,
                                          'rectangle': parse_location_pair,
                                          'start_date': parse_isodate,
                                          'end_date': parse_isodate,
                                          'start_time': parse_isotime,
                                          'end_time': parse_isotime})
        return jsonify(SummaryService.get_nta2020_summary(**arguments))

    @app.route('/api/boro_summary.json', methods=['GET'])
    def boro_summary_as_json() -> Response:
        arguments = get_all_request_args({'boro_id': int,
                                          'rectangle': parse_location_pair,
                                          'start_date': parse_isodate,
                                          'end_date': parse_isodate,
                                          'start_time': parse_isotime,
                                          'end_time': parse_isotime})
        return jsonify(SummaryService.get_boro_summary(**arguments))

    @app.route('/api/city_summary.json', methods=['GET'])
    def city_summary_as_json() -> Response:
        arguments = get_all_request_args({'start_date': parse_isodate,
                                          'end_date': parse_isodate,
                                          'start_time': parse_isotime,
                                          'end_time': parse_isotime})
        return jsonify(SummaryService.get_city_summary(**arguments))

    return app


flask_app = create_app()

if __name__ == '__main__':
    flask_app.run(debug=(getenv('FLASK_ENV') == 'development' or getenv('FLASK_DEBUG').lower() == 'true'))
    