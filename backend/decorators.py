from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Skip JWT validation for OPTIONS requests to allow CORS preflight
        if request.method == 'OPTIONS':
            return {}, 200  # Return empty response to let flask-cors add headers
        verify_jwt_in_request()
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()
        if not user or user.role != 'admin':
            return ({"msg": "Admin access only"}), 403
        return fn(*args, **kwargs)
    return wrapper