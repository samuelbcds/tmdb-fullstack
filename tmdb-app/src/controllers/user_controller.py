from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime as dt
from src import db
from src.models.user import User
from src.errors import error_response


def create_user():
    if not request.is_json:
        return error_response(400, "Request must be JSON")
    
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    admin = data.get('admin', False)

    if not name or not email or not password:
        return error_response(400, "Name, email and password are required")
    
    if '@' not in email or '.' not in email:
        return error_response(400, "Invalid email format")
    
    if User.query.filter_by(name=name).first():
        return error_response(409, "Name already exists")
    
    if User.query.filter_by(email=email).first():
        return error_response(409, "Email already exists")
    
    try:
        new_user = User(
            name=name,
            email=email,
            password='',
            created_at=dt.now(),
            admin=admin
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return error_response(500, f"Error creating user: {str(e)}")


@jwt_required()
def get_users():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        per_page = min(per_page, 100)
        
        pagination = User.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        users = [user.to_dict() for user in pagination.items]
        
        return jsonify({
            'users': users,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        return error_response(500, f"Error fetching users: {str(e)}")


@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return error_response(404, "User not authenticated")
        
        return jsonify({
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return error_response(500, f"Error fetching user: {str(e)}")

