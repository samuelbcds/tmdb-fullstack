import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from src.config.config import config
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy


jwt = JWTManager()
db = SQLAlchemy()

def create_app(config_name=None):
    
    app = Flask(__name__)
    
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app.config.from_object(config.get(config_name, config['default']))
    
    CORS(app,
         origins=app.config.get('CORS_ORIGINS'),
         supports_credentials=app.config.get('CORS_SUPPORTS_CREDENTIALS', True),
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         allow_headers=[
             'Content-Type',
             'Authorization',
             'Access-Control-Allow-Credentials',
             'X-Requested-With',
             'Accept'
         ],
         expose_headers=['Content-Range', 'X-Content-Range'],
         max_age=app.config.get('CORS_MAX_AGE', 3600))
    
    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        from src.routes import routes
        db.create_all()
    
    from src.routes.routes import api
    app.register_blueprint(api, url_prefix='/api')

    return app  