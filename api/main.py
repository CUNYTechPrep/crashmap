from datetime import date, time
from os import getenv
from flask import Flask, jsonify, make_response, request, Response
from werkzeug.exceptions import BadRequest

from models import Boro, BoroSummary, Collision, db, H3, H3Summary, NTA2020, NTA2020Summary, Person, Summary, Vehicle
from services import CustomEncoder


def create_app() -> Flask:  # TODO: Move views to a separate file
    app = Flask(__name__,
                static_folder='../client/build',  # The React app is served from this local path.
                static_url_path='/')
    app.json_encoder = CustomEncoder
    db_uri = {component: getenv(f'DATABASE_{component}')
              for component in ('SCHEME', 'HOST', 'PORT', 'USERNAME', 'PASSWORD', 'NAME')}
    app.config['SQLALCHEMY_DATABASE_URI'] = '{SCHEME}://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{NAME}'.format(**db_uri)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # TODO: Initialize services here.

    def make_geojson_response(obj: dict | list) -> Response:
        response = make_response({'type': 'FeatureCollection',
                                  'features': obj}
                                 if type(obj) is list
                                 else obj)
        response.headers['Content-type'] = 'application/geo+json'
        return response

    @app.route('/')
    def index() -> Response:
        return app.send_static_file('index.html')

    @app.route('/api/boro.geojson', methods=['GET'])
    def boro_as_geojson() -> Response:
        query = db.session.query(Boro)
        if (id := request.args.get('id', None, int)) is not None:
            query = query.filter(Boro.id == id)
        return make_geojson_response(query.all())

    @app.route('/api/nta2020.geojson', methods=['GET'])
    def nta2020_as_geojson() -> Response:
        query = db.session.query(NTA2020)
        if (id := request.args.get('id', None, str)) is not None:
            query = query.filter(NTA2020.id == id)
        if (boro_id := request.args.get('boro_id', None, int)) is not None:
            query = query.filter(NTA2020.boro_id == boro_id)
        return make_geojson_response(query.all())

    @app.route('/api/h3.geojson', methods=['GET'])
    def h3_as_geojson() -> Response:
        query = db.session.query(H3)
        if (h3_index := request.args.get('h3_index', None, int)) is not None:
            query = query.filter(H3.h3_index == h3_index)
        if (nta2020_id := request.args.get('nta2020_id', None, int)) is not None:
            query = query.filter(H3.nta2020s.any(id=nta2020_id))
        if (boro_id := request.args.get('boro_id', None, int)) is not None:
            query = query.filter(H3.nta2020s.any(boro_id=boro_id))
        return make_geojson_response(query.all())

    @app.route('/api/collision.geojson', methods=['GET'])
    def collision_as_geojson() -> Response:
        query = db.session.query(Collision)
        return jsonify(query.all())

    @app.route('/api/summary.json', methods=['GET'])
    def summary_as_json() -> Response:
        h3_index = request.args.get('h3_index', None, int)
        nta2020_id = request.args.get('nta2020_id', None, int)
        boro_id = request.args.get('boro_id', None, int)
        if h3_index is not None and nta2020_id is not None or \
           h3_index is not None and boro_id is not None or \
           nta2020_id is not None and boro_id is not None:
            raise BadRequest('h3_index, nta2020_id, and boro_id are mutually exclusive parameters.')
        if h3_index is not None:
            model = H3Summary
            query = db.session.query(model) \
                              .filter(H3Summary.h3_index == h3_index)
        elif nta2020_id is not None:
            model = NTA2020Summary
            query = db.session.query(model) \
                              .filter(NTA2020Summary.nta2020_id == nta2020_id)
        elif boro_id is not None:
            model = BoroSummary
            query = db.session.query(model) \
                              .filter(BoroSummary.boro_id == boro_id)
        else:
            model = Summary
            query = db.session.query(Summary)
        start_date = request.args.get('start_date', None, date.fromisoformat)
        end_date = request.args.get('end_date', None, date.fromisoformat)
        if start_date is not None:
            query = query.filter(model.date >= start_date)
        if end_date is not None:
            query = query.filter(model.date <= end_date)
        return jsonify(query.all())

    return app


flask_app = create_app()

if __name__ == '__main__':
    flask_app.run(debug=(getenv('FLASK_ENV') == 'development' or getenv('FLASK_DEBUG').lower() == 'true'))
