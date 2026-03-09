from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, set_refresh_cookies,
    unset_access_cookies, unset_jwt_cookies
)
from src import jwt, db
from src.models.user import User
from src.errors import error_response


blacklist = set()


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    return jwt_payload["jti"] in blacklist


def login():
    if not request.is_json:
        return error_response(400)

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return error_response(400, "Email or password missing.")

    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        return error_response(401, "Email or password invalid.")

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))
    
    response = jsonify(
        message="Login successful",
        user={
            "id": str(user.id),
            "name": user.name,
            "email": user.email
        }
    )
    
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)
    
    return response


@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return error_response(401, "Unknown user.")
    
    access_token = create_access_token(identity=str(user.id))
    
    response = jsonify(message="Token refreshed successfully")
    set_access_cookies(response, access_token)
    
    return response


# revoke current access token
@jwt_required()
def logout_access_token():
    blacklist.add(get_jwt()["jti"])
    
    response = jsonify(message="Successfully logged out.")
    unset_access_cookies(response)
    
    return response


# revoke current refresh token
@jwt_required(refresh=True)
def logout_refresh_token():
    blacklist.add(get_jwt()["jti"])
    
    response = jsonify(message="Successfully logged out.")
    unset_jwt_cookies(response)
    
    return response