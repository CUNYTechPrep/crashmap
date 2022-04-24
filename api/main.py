import csv
from io import StringIO
from os import environ, getenv
from typing import Any, Optional

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

    DATABASE_SCHEME = getenv('DATABASE_SCHEME')
    DATABASE_HOST = getenv('DATABASE_HOST')
    DATABASE_PORT = getenv('DATABASE_PORT')
    DATABASE_USERNAME = getenv('DATABASE_USERNAME')
    DATABASE_PASSWORD = getenv('DATABASE_PASSWORD')
    DATABASE_NAME = getenv('DATABASE_NAME')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'{DATABASE_SCHEME}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # TODO: Initialize services here.

    # See the Stack Overflow answer for why this is needed: https://stackoverflow.com/a/44572672/1405571.
    @app.after_request
    def add_cors_headers(response: Response) -> Response:
        if request.referrer and url_parse(request.referrer[:-1]).host == request.host:
            response.headers.add('Access-Control-Allow-Origin', request.host_url)
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
            response.headers.add('Access-Control-Allow-Headers', 'Cache-Control')
            response.headers.add('Access-Control-Allow-Headers', 'X-Requested-With')
            response.headers.add('Access-Control-Allow-Headers', 'Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS, POST')
        return response

    @app.errorhandler(HTTPException)
    def errorhandler(exception: HTTPException):
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
        print(f'Returning result of ({query.statement.columns.keys()})')
        with StringIO() as string_io:
            csv_writer = csv.writer(string_io)
            csv_writer.writerow(query.statement.columns.keys())
            csv_writer.writerows(query.all())
            response = make_response(string_io.getvalue())
            response.headers['Content-type'] = 'text/csv'
            return response

    @app.route('/api/boro.geojson', methods=['GET'])
    def boro_as_geojson() -> dict[str, Any]:
        boro_code = request.args.get('boro_code', None, int)
        query = db.session.query(func.ST_AsGeoJSON(BoroModel))
        if boro_code != None:
            query = query.filter(BoroModel.boro_code == boro_code)
        return {"type": "FeatureCollection",
                "features": [json.loads(boro[0]) for boro in query.all()]}

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
    flask_app.run(debug=(getenv('FLASK_ENV') == 'development'))
