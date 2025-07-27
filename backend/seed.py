from app import create_app
from extensions import db
from models import User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime, timedelta
import pytz
import os

# Timezone
ist = pytz.timezone('Asia/Kolkata')

# Create app and context
app = create_app()

with app.app_context():
    
    # Create regular users
    users = [
        User(name="Alice", email="alice@mail.com", password="pass123", vehicleno="TS 12 AB 1234", role="user"),
        User(name="Bob", email="bob@mail.com", password="pass123", vehicleno="TS 12 CD 5678", role="user"),
        User(name="Charlie", email="charlie@mail.com", password="pass123", vehicleno="TS 12 EF 9012", role="user"),
    ]
    db.session.add_all(users)
    db.session.commit()
    print("Users added")

    # Create parking lots
    lots = [
        ParkingLot(area="Hitex", price=50, address="123 Main St", pin_code="600001", capacity=5, available=5),
        ParkingLot(area="Gachibowli", price=40, address="456 Tech Rd", pin_code="600002", capacity=4, available=4)
    ]
    db.session.add_all(lots)
    db.session.commit()
    print("Parking lots added")

    # Create parking spots
    for lot in lots:
        for _ in range(lot.capacity):
            spot = ParkingSpot(lot_id=lot.id, status='A')
            db.session.add(spot)
    db.session.commit()
    print("Parking spots added")

    # Create reservations
    spots = ParkingSpot.query.filter_by(status='A').limit(3).all()
    users_list = User.query.filter_by(role='user').all()

    for i, (user, spot) in enumerate(zip(users_list, spots)):
        leaving_timestamp = None  # Active reservation
        res = Reservation(
            spot_id=spot.id,
            lot_id=spot.lot_id,
            user_id=user.id,
            parking_timestamp=datetime.now(ist) - timedelta(hours=2),
            leaving_timestamp=leaving_timestamp,
            parking_cost=2 * ParkingLot.query.get(spot.lot_id).price
        )
        spot.status = 'O'
        spot.lot.available -= 1
        db.session.add(res)
    db.session.commit()
    print("Reservations added")

    print("Data Insertion completed successfully.")
