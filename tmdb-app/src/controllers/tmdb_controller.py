import json
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from flask import current_app, jsonify, request

from src.errors import error_response


_ALLOWED_TMDB_PATHS = {
    'genre/movie/list',
    'search/movie',
    'discover/movie',
    'movie/popular',
}
_MOVIE_DETAILS_PATH = re.compile(r'^movie/\d+$')


def _is_allowed_tmdb_path(tmdb_path: str) -> bool:
    return tmdb_path in _ALLOWED_TMDB_PATHS or bool(_MOVIE_DETAILS_PATH.match(tmdb_path))


def _build_tmdb_auth_headers() -> dict:
    bearer_token = current_app.config.get('TMDB_BEARER_TOKEN')
    headers = {
        'Accept': 'application/json',
    }
    if bearer_token:
        headers['Authorization'] = f'Bearer {bearer_token}'
    return headers


def _build_tmdb_url(tmdb_path: str, params: dict) -> str:
    base_url = current_app.config.get('TMDB_API_BASE_URL', 'https://api.themoviedb.org/3').rstrip('/')
    query_params = dict(params)

    has_bearer = bool(current_app.config.get('TMDB_BEARER_TOKEN'))
    api_key = current_app.config.get('TMDB_API_KEY')
    if not has_bearer and api_key:
        query_params['api_key'] = api_key

    query_string = urlencode(query_params, doseq=True)
    url = f"{base_url}/{tmdb_path}"
    if query_string:
        url = f"{url}?{query_string}"
    return url


def _proxy_tmdb_get(tmdb_path: str, params: dict):
    has_any_credential = bool(
        current_app.config.get('TMDB_BEARER_TOKEN') or current_app.config.get('TMDB_API_KEY')
    )
    if not has_any_credential:
        return error_response(500, 'TMDB credentials are not configured on the server')

    url = _build_tmdb_url(tmdb_path, params)
    req = Request(url, headers=_build_tmdb_auth_headers(), method='GET')
    timeout = current_app.config.get('TMDB_TIMEOUT_SECONDS', 10)

    try:
        with urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode('utf-8'))
            status = response.getcode()
            return jsonify(payload), status
    except HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode('utf-8'))
            message = payload.get('status_message') or payload.get('message') or 'TMDB request failed'
        except Exception:
            message = 'TMDB request failed'
        return error_response(exc.code, message)
    except URLError:
        return error_response(502, 'Unable to reach TMDB service')
    except Exception as exc:
        return error_response(500, f'Unexpected TMDB proxy error: {str(exc)}')


def tmdb_proxy_get(tmdb_path: str):
    normalized_path = tmdb_path.strip('/')
    if not _is_allowed_tmdb_path(normalized_path):
        return error_response(403, 'TMDB endpoint is not allowed')

    return _proxy_tmdb_get(normalized_path, request.args.to_dict(flat=True))
