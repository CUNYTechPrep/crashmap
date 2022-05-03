from datetime import date, time
from os import getenv
from flask import Flask, jsonify, make_response, request, Response

from models import db
from services import BoroService, CollisionService, CustomEncoder, H3Service, NTA2020Service, SummaryService


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
        id = request.args.get('id', None, int)
        return make_geojson_response(BoroService.get_boro(id))

    @app.route('/api/nta2020.geojson', methods=['GET'])
    def nta2020_as_geojson() -> Response:
        id = request.args.get('id', None, str)
        boro_id = request.args.get('boro_id', None, int)
        return make_geojson_response(NTA2020Service.get_nta2020(id, boro_id))

    @app.route('/api/h3.geojson', methods=['GET'])
    def h3_as_geojson() -> Response:
        h3_index = request.args.get('h3_index', None, int)
        k = request.args.get('k', None, int)
        nta2020_id = request.args.get('nta2020_id', None, str)
        boro_id = request.args.get('boro_id', None, int)
        only_water = request.args.get('only_water', None, bool)
        return make_geojson_response(H3Service.get_h3(h3_index, k, nta2020_id, boro_id, only_water))

    @app.route('/api/collision.json', methods=['GET'])
    def collision_as_geojson() -> Response:
        id = request.args.get('id', None, int)
        return jsonify(CollisionService.get_collision(id))

    @app.route('/api/summary.json', methods=['GET'])
    def summary_as_json() -> Response:
        h3_index = request.args.get('h3_index', None, int)
        nta2020_id = request.args.get('nta2020_id', None, str)
        boro_id = request.args.get('boro_id', None, int)
        start_date = request.args.get('start_date', None, date.fromisoformat)
        end_date = request.args.get('end_date', None, date.fromisoformat)
        return jsonify(SummaryService.get_summary(h3_index, nta2020_id, boro_id, start_date, end_date))

    return app


flask_app = create_app()

if __name__ == '__main__':
    flask_app.run(debug=(getenv('FLASK_ENV') == 'development' or getenv('FLASK_DEBUG').lower() == 'true'))
