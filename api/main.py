import csv
from io import StringIO
from os import environ, getenv
from typing import Any, Iterable, Optional

from flask import Flask, json, jsonify, make_response, request, Response
from geoalchemy2 import func
from werkzeug.exceptions import HTTPException
from werkzeug.urls import url_parse

from models import db, BoroModel

# Import services here.


def create_app() -> Flask:  # TODO: Move views to a separate file
    app = Flask(__name__,
                static_folder='../client/build',  # The React app is served from this local path.
                static_url_path='/')
    db_uri = {component: getenv(f'DATABASE_{component}')
              for component in ('SCHEME', 'HOST', 'PORT', 'USERNAME', 'PASSWORD', 'NAME')}
    app.config['SQLALCHEMY_DATABASE_URI'] = '{SCHEME}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{NAME}'.format(**db_uri)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # TODO: Initialize services here.

    def make_csv_response(header: Iterable, rows: Iterable[Iterable]) -> Response:
        with StringIO() as string_io:
            csv_writer = csv.writer(string_io)
            csv_writer.writerow(header)
            csv_writer.writerows(rows)
            response = make_response(string_io.getvalue())
            response.headers['Content-type'] = 'text/csv'
            return response

    def make_json_response(obj: dict | list, is_geojson: bool = False) -> Response:
        response = make_response(obj)
        response.headers['Content-type'] = 'application/geo+json' if is_geojson else 'application/json'
        return response

    @app.errorhandler(HTTPException)
    def errorhandler(exception: HTTPException) -> Response | tuple[HTTPException, int]:
        if app.debug:
            return Response({'error': str(exception)}, 500)
        return exception, 500

    @app.route('/')
    def index() -> Response:
        return app.send_static_file('index.html')

    @app.route('/api/boro.csv', methods=['GET'])
    def boro_as_csv() -> Response:
        boro_code = request.args.get('boro_code', None, int)
        query = db.session.query(BoroModel.boro_code,
                                 BoroModel.boro_name,
                                 BoroModel.shape_leng,
                                 BoroModel.shape_area,
                                 func.ST_AsText(BoroModel.the_geom).label('the_geom'))
        if boro_code != None:
            query = query.filter(BoroModel.boro_code == boro_code)
        return make_csv_response(query.statement.columns.keys(), query.all())

    @app.route('/api/boro.geojson', methods=['GET'])
    def boro_as_geojson() -> Response:
        boro_code = request.args.get('boro_code', None, int)
        query = db.session.query(func.ST_AsGeoJSON(BoroModel))
        if boro_code != None:
            query = query.filter(BoroModel.boro_code == boro_code)
        return make_json_response({'type': 'FeatureCollection',
                                   'features': [json.loads(boro[0]) for boro in query.all()]},
                                  is_geojson=True)

    @app.route('/api/summary', methods=['GET'])
    def suggestion() -> Response:
        return 'This is a summy summary.'  # TODO: Return actual results.

    @app.route('/api/details', methods=['GET'])
    def details() -> Response:
        return 'These are detailed details.'  # TODO: Return actual results.

    @app.route('/api/environment', methods=['GET'])
    def environment() -> Response:
        return jsonify(dict(environ))

    return app


flask_app = create_app()

if __name__ == '__main__':
    flask_app.run(debug=(getenv('FLASK_ENV') == 'development' or getenv('FLASK_DEBUG').lower() == 'true'))
