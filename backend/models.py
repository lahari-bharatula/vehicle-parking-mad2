from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db=SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password=db.Column(db.String(100), nullable=False)
    vehicleno=db.Column(db.String(100))
    role = db.Column(db.String(10), default='user')  # 'admin' or 'user'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'vehicleno': self.vehicleno,
            'role': self.role
        }

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    id = db.Column(db.Integer, primary_key=True)
    area = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(6), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    available=db.Column(db.Integer, nullable=False)

    spots = db.relationship('ParkingSpot', backref='lot', lazy=True, cascade='all,delete-orphan')
    reservations = db.relationship('Reservation', backref='lot', lazy=True)
class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), nullable=False)  # 'A' for available, 'O' for occupied
    
    reservations = db.relationship('Reservation', backref='spot', cascade='all,delete-orphan')
    def to_dict(self):
        reservation = Reservation.query.filter_by(spot_id=self.id).first()
        return {
            'spot_id': self.id,
            'lot_id': self.lot_id,
            'status': self.status,
            'reservation_id': reservation.id if reservation else None,
            'user_id': reservation.user_id if reservation else None
        }
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parking_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    leaving_timestamp = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float)
    
    user = db.relationship('User', backref='reservations')


