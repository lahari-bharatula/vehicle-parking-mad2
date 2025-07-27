from flask import request
from flask_jwt_extended import create_access_token
from flask_restful import Resource

from backend.models import User

class UserResource(Resource):
    pass

class loginResource(Resource):
    
    def post(self):
        data = request.get_json()
        print("Received login data:", data)

        email=data.get('email', None)
        password=data.get('password', None)
        if not email or not password:
            return {"error": "please provide all required info"}, 400
        user =User.query.filter_by(email=email).first()
        if not user:
            return{"error": "user doesnt exist"}, 400
        if user.password!=password:
            return {'message': "Invalid credentials!"}, 401
        token=create_access_token(identity=user.email)
        return {
            "token": token,
            "user": {
                "email": user.email,
                "role": user.role
            }
        }, 200