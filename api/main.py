from flask import Flask, jsonify, request, Response
from werkzeug.exceptions import HTTPException
from werkzeug.urls import url_parse
# Import services here.


def create_app() -> Flask:  # TODO: Move views to a separate file
    app = Flask(__name__,
                static_folder='../client/build',  # The React app is served from this local path.
                static_url_path='/')

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

    @app.route('/api/summary', methods=['GET'])
    def suggestion() -> Response:
        return 'This is a summy summary.'  # TODO: Return actual results.

    @app.route('/api/details', methods=['GET'])
    def details() -> Response:
        return 'These are detailed details.'  # TODO: Return actual results.

    return app


flask_app = create_app()

if __name__ == '__main__':
    flask_app.run()
