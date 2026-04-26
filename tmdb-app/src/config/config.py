from os import environ, path
from dotenv import load_dotenv
from datetime import timedelta

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '../../.env'))


def _parse_cors_origins(default_origins):
    raw_origins = environ.get('CORS_ORIGINS', '').strip()
    if not raw_origins:
        return default_origins
    return [origin.strip() for origin in raw_origins.split(',') if origin.strip()]


class Config:
    
    # General Config
    SECRET_KEY = environ.get('SECRET_KEY')
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get('FLASK_ENV')

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # TMDB configuration (server-side only)
    TMDB_API_BASE_URL = environ.get('TMDB_API_BASE_URL', 'https://api.themoviedb.org/3')
    TMDB_API_KEY = environ.get('TMDB_API_KEY')
    TMDB_BEARER_TOKEN = environ.get('TMDB_BEARER_TOKEN')
    TMDB_TIMEOUT_SECONDS = float(environ.get('TMDB_TIMEOUT_SECONDS', '10'))
    
    # JWT Configuration
    JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # JWT HTTP-only
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_COOKIE_SECURE = False  
    JWT_COOKIE_CSRF_PROTECT = False  
    JWT_COOKIE_SAMESITE = 'Lax' 
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/'
    JWT_SESSION_COOKIE = False  
    
    # CORS Configuration
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_MAX_AGE = 3600
    CORS_ORIGINS = _parse_cors_origins([
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:5174',
        'http://localhost:8080'
    ])


class ProductionConfig(Config):
    
    DEBUG = False
    TESTING = False
    
    # CORS 
    CORS_ORIGINS = _parse_cors_origins([])
    
    # JWT cookies HTTP-only
    JWT_COOKIE_SECURE = True 
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_COOKIE_SAMESITE = 'None'  
    
    # Database
    SQLALCHEMY_ECHO = False


config = {
    'production': ProductionConfig,
    'default': Config
}