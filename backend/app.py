from flask import Flask
from flask_restful import Resource, Api
from flask_cors import CORS
from models import db, ParkingLot, User
from controller import ParkingResource, SpotResource,ReservationResource, loginResource, UserResource, cache
from flask_jwt_extended import JWTManager

app=Flask(__name__)
CORS(app, supports_credentials=True,resources={
    r"/*": {
        "origins": ["http://localhost:5173"],  
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

api=Api(app)


app.config["JWT_SECRET_KEY"] = "l1997"
jwt = JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
db.init_app(app)

api.add_resource(ParkingResource, '/lots', '/lots/<lot_id>')
api.add_resource(SpotResource,'/lots/<lot_id>/<spot_id>')
api.add_resource(ReservationResource, '/reservations', '/reservations/<int:reservation_id>')
api.add_resource(UserResource, '/users', '/users/<int:user_id>')
api.add_resource(loginResource, '/login')

#caching
app.config["CACHE_TYPE"]="RedisCache"
app.config["CACHE_REDIS_URL"]='redis://localhost:6379/0'
cache.init_app(app)

def create_admin_user():
    """Create an admin user if none exists."""
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                name="Admin User",
                email="admin@park.com",
                password="admin123",
                role="admin" 
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")


if __name__=="__main__":
    with app.app_context():
        db.create_all()
        create_admin_user()
        app.run(debug=True)