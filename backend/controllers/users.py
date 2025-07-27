from flask import request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_restful import Resource

from models import User
from extensions import db

class UserResource(Resource):
    @jwt_required()
    def get(self, user_id=None):
        identity = get_jwt_identity()
        print("JWT Identity:", identity)

        if user_id:
            user = User.query.get(user_id)
            if user:
                return {
                    "msg": "user found",
                    "email": user.email,
                    "name": user.name,
                    "vehicleno": user.vehicleno,
                    "role": user.role
                }, 200
            return {"error": "user not found"}, 404

        # No user_id provided → Admin access check
        current_user = User.query.filter_by(email=identity).first()
        if not current_user or current_user.role != "admin":
            return {"msg": "Admin access only"}, 403

        users = User.query.all()
        print("Users queried:", users)

        users_list = []
        for user in users:
            user_dict = {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "vehicleno": user.vehicleno,
                "role": user.role
            }
            print("User dict:", user_dict)
            users_list.append(user_dict)

        return {"msg": "all users", "users": users_list}, 200

    def post(self):
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')  
        vehicleno=data.get('vehicleno')
        role = 'user' 

        if not email or not name or not password:
            return {'msg': "Please provide all required information!"}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'msg': "User already exists!"}, 400


        new_user = User(email=email, name=name, password=password, vehicleno=vehicleno, role=role)
        db.session.add(new_user)
        db.session.commit()

        return {'msg': "Successfully registered user!"}, 201

    @jwt_required()
    def put(self, user_id=None):
        
        if not user_id:
            return {'msg': "User id is required to update!"}, 400

        current_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_email).first()

        if not current_user or current_user.id != user_id:
            return {'msg': "Unauthorized to update this user!"}, 403

        user = User.query.get(user_id)
        if not user:
            return {'msg': "User does not exist to update!"}, 404

        data = request.get_json()

        updated_fields = []
        if 'name' in data:
            user.name = data['name']
            updated_fields.append('name')
        if 'email' in data:
            user.email = data['email']
            updated_fields.append('email')
        if 'password' in data:
            user.password = data['password']  
            updated_fields.append('password')
        if 'vehicleno' in data:
            user.vehicleno = data['vehicleno']
            updated_fields.append('vehicleno')

        if not updated_fields:
            return {'msg': "Provide at least one field to update!"}, 400

        db.session.commit()

        return {
            'msg': "User information updated!",
            'updated_fields': updated_fields,
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'vehicleno': user.vehicleno,
                'role': user.role
            }
        }, 200


    @jwt_required()
    def delete(self, user_id=None):
        if not user_id:
            return {'msg': "User id is required to delete!"}, 400

        current_email = get_jwt_identity()
        current_user = User.query.filter_by(email=current_email).first()

        if not current_user or current_user.id != user_id:
            return {'msg': "Unauthorized to delete this user!"}, 403

        user = User.query.get(user_id)
        if not user:
            return {'msg': "User does not exist to delete!"}, 404

        db.session.delete(user)
        db.session.commit()
        return {'msg': "User has been deleted!"}, 200

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