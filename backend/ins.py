from app import app
from models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timedelta
import random
import pytz

ist = pytz.timezone('Asia/Kolkata')

with app.app_context():

    # Create regular users (admin is created in app.py)
    users = [
        User(name="Alice", email="alice@example.com", password="pass123",vehicleno="TS 12 AB 1234"),
        User(name="Bob", email="bob@example.com", password="pass123", vehicleno="TS 12 CD 5678"),
        User(name="Charlie", email="charlie@example.com", password="pass123", vehicleno="TS 12 EF 9012"),
    ]

    db.session.add_all(users)
    db.session.commit()

    # Create Parking Lots
    lots = [
        ParkingLot(area="Downtown", price=50, address="123 Main St", pin_code="600001", capacity=5, available=5),
        ParkingLot(area="Tech Park", price=40, address="456 Tech Rd", pin_code="600002", capacity=4, available=4)
    ]
    
    db.session.add_all(lots)
    db.session.commit()

    # Create Parking Spots for each lot
    for lot in lots:
        for _ in range(lot.capacity):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)
    db.session.commit()

    # Create some Reservations (mix of active and past)
    spots = ParkingSpot.query.filter_by(status='A').limit(3).all()
    users_list = User.query.filter_by(role='user').all()

    for i, (user, spot) in enumerate(zip(users_list, spots)):
        # First reservation is active (leaving_timestamp=None)
        # Others are past (leaving_timestamp set)
        leaving_timestamp = None 
        res = Reservation(
            spot_id=spot.id,
            lot_id=spot.lot_id,  # Set lot_id from spot
            user_id=user.id,  # Use User.id, not email
            parking_timestamp=datetime.now(ist) - timedelta(hours=2),
            leaving_timestamp=leaving_timestamp,
            parking_cost=spot.lot.price * 2
        )
        spot.status = 'O'
        spot.lot.available -= 1
        db.session.add(res)
    db.session.commit()
    print("Data inserted successfully.")