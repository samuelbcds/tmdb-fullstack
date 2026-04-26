from flask import Blueprint, jsonify
from src.controllers.auth import *
from src.controllers.user_controller import *
from src.controllers.movie_controller import *
from src.controllers.tmdb_controller import *


api = Blueprint('api', __name__)

@api.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@api.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'TMDB App API ON'}), 200

@api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal error'}), 500

#################### Authentication routes ###################

@api.route('/login', methods=['POST'])
def login_route():
    return login()

@api.route('/refresh', methods=['POST'])
def refresh_route():
    return refresh()

@api.route('/logout', methods=['DELETE'])
def logout_access_route():
    return logout_access_token()    

@api.route('/logout2', methods=['DELETE'])
def logout_refresh_route():
    return logout_refresh_token()

#################### User routes ###################

@api.route('/users', methods=['POST'])
def create_user_route():
    return create_user()


@api.route('/users/me', methods=['GET'])
def get_current_user_route():
    return get_current_user()



#################### Movie routes ###################

@api.route('/tmdb/<path:tmdb_path>', methods=['GET'])
def tmdb_proxy_route(tmdb_path):
    return tmdb_proxy_get(tmdb_path)

@api.route('/movies', methods=['POST'])
def create_movie_route():
    return create_movie()

@api.route('/movies', methods=['GET'])
def get_movies_route():
    return get_movies_rated()

@api.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie_route(movie_id):
    return get_movie(movie_id)

@api.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie_route(movie_id):
    return delete_movie(movie_id)

@api.route('/movies/<int:movie_id>/rate', methods=['PUT'])
def rate_movie_route(movie_id):
    return re_rate_movie(movie_id)