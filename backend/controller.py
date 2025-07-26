from flask import request
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from flask_restful import Resource
from models import db, User, ParkingLot, ParkingSpot, Reservation
from datetime import datetime
from utils import admin_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_caching import Cache

cache = Cache()

import time

class ParkingResource(Resource):
    @cache.cached(timeout=60, key_prefix="AvailableLots") 
    @admin_required
    def get(self, lot_id=None):
        #time.sleep(5)
        try:
            if lot_id:
                plot = ParkingLot.query.get(lot_id)
                if plot:
                    occupied = ParkingSpot.query.filter_by(lot_id=plot.id, status='O').count()
                    return {
                        'msg': 'lot found',
                        'lot': plot.id,
                        'area': plot.area,
                        'pin code': plot.pin_code,
                        'available': plot.available,
                        'capacity': plot.capacity,
                        'occupied': occupied,
                        'price': plot.price
                    }
                return {'msg': 'parking lot not found'}, 404
            lots = ParkingLot.query.all()
            lots = [{
                'lot': lot.id,
                'area': lot.area,
                'price': lot.price,
                'pin_code': lot.pin_code,
                'available': lot.available,
                'capacity': lot.capacity,
                'spots': [  
            {'id': spot.id, 'status': spot.status} for spot in lot.spots
        ],
                'occupied': ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            } for lot in lots]
            return {'msg': "all parking lots", "parking lots": lots}
        except Exception as e:
            print(f"Error in ParkingResource.get: {str(e)}")
            return {"msg": f"Failed to fetch lots: {str(e)}"}, 500
    
    @admin_required
    def post(self):
        #admin-only
        #creating a parking lot, along with parking spots 
        data=request.get_json()
        lid=data.get('l_id', None)
        loc=data.get('area', None)
        price=data.get('price', None)
        address=data.get('address', None)
        pin=data.get('pin', None)
        spots=data.get('available', None)
    
        if spots is None or spots < 0:
            return {"error": "number_of_spots must be provided and non-negative"}, 400
        if not loc or not price or not address or not pin:
            return {'msg': "All fields (area, price, address, pin, available) are required."}, 400

        
        lot=ParkingLot.query.get(lid)
        if lot:
            return{"msg": "this parking lot already exists" }, 400
        plot=ParkingLot(id=lid,
                        area=loc,
                        price=price, 
                        address=address, 
                        pin_code=pin, 
                        capacity=spots,
                        available=spots )
        db.session.add(plot)
        db.session.commit()

        for _ in range(spots):
            spot = ParkingSpot(lot_id=plot.id, status='A')  # A = Available
            db.session.add(spot)

        db.session.commit()  # Commiting all the spots
        cache.delete('AvailableLots')
        return {"message": "Parking lot and spots created", "lot_id": plot.id}, 201

    @admin_required
    def put(self, lot_id):
        try:
            cache.delete('AvailableLots')
            if not lot_id:
                return {"msg": "lot id is required to update"}, 400
            data = request.get_json()
            print(f"Received data: {data}")
            lot = ParkingLot.query.get_or_404(lot_id)

            new_capacity = data.get('capacity')
            if new_capacity is None:
                return {"msg": "capacity is required"}, 400
            if new_capacity < 0:
                return {"msg": "capacity must be non-negative"}, 400

            # Update lot fields
            lot.area = data.get('area', lot.area)
            lot.price = data.get('price', lot.price)
            lot.address = data.get('address', lot.address)
            lot.pin_code = data.get('pin_code', lot.pin_code)

            # Calculate current spot counts
            total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
            occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
            current_available = total_spots - occupied_spots

            print(f"Updating lot {lot_id}: total_spots={total_spots}, occupied_spots={occupied_spots}, current_available={current_available}, new_capacity={new_capacity}")

            # Validate new_capacity
            if new_capacity < occupied_spots:
                return {"msg": f"Cannot set capacity to {new_capacity}. There are {occupied_spots} occupied spots."}, 400

            # Adjust spots to match new_capacity
            diff = new_capacity - total_spots
            if diff > 0:
                # Add new available spots
                for _ in range(diff):
                    new_spot = ParkingSpot(lot_id=lot.id, status='A')
                    db.session.add(new_spot)
            elif diff < 0:
                # Remove excess spots (only available spots can be removed)
                removable_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(abs(diff)).all()
                if len(removable_spots) < abs(diff):
                    return {"msg": f"Not enough available spots to remove. Need {abs(diff)}, found {len(removable_spots)}"}, 400
                for spot in removable_spots:
                    db.session.delete(spot)

            # Update capacity and recalculate available
            lot.capacity = new_capacity
            lot.available = new_capacity - occupied_spots  # Derive available from new capacity and occupied spots
            db.session.commit()
            print(f"Updated lot {lot_id}: available={lot.available}, capacity={lot.capacity}")
            return {"msg": "Parking lot updated successfully"}
        except Exception as e:
            db.session.rollback()
            print(f"Error in ParkingResource.put: {str(e)}")
            return {"msg": f"Failed to update lot: {str(e)}"}, 500

    @admin_required
    def delete(self, lot_id=None):
      try:
        print(f"Starting deletion of lot {lot_id}")
        cache.delete('AvailableLots')
        if not lot_id:
            return {"msg": "lot id is required to delete"}, 400
        
        # Start a new session to avoid interference
        db.session.expire_all()
        
        lot = ParkingLot.query.get(lot_id)
        if not lot:
            return {"msg": "lot not found"}, 404
        
        # Get all spot IDs for the lot
        spots = ParkingSpot.query.filter_by(lot_id=lot_id).all()
        print(f"Lot {lot_id} has {len(spots)} spots: {[s.id for s in spots]}")
        print(f"Session before delete: dirty={db.session.dirty}, deleted={db.session.deleted}, new={db.session.new}")
        
        # Check for active reservations (leaving_timestamp IS NULL)
        spot_ids = [spot.id for spot in spots]
        active_reservations = db.session.execute(
            select(Reservation)
            .where(Reservation.spot_id.in_(spot_ids))
            .where(Reservation.leaving_timestamp.is_(None))
        ).scalars().first()
        
        if active_reservations:
            return {"msg": "Cannot delete lot with active reservations"}, 400
        
        # Delete the lot (spots and reservations deleted via cascades)
        db.session.delete(lot)
        print(f"Session after lot deletion: dirty={db.session.dirty}, deleted={db.session.deleted}, new={db.session.new}")
        
        db.session.commit()
        print(f"Successfully deleted lot {lot_id}")
        return {"msg": "parking lot has been deleted"}
      except Exception as e:
        db.session.rollback()
        print(f"Error during deletion: {str(e)}")
        return {"msg": f"Failed to delete lot: {str(e)}"}, 500

class ReservationResource(Resource):
    @jwt_required
    def get(self, reservation_id=None):
        try:
            user_email = get_jwt_identity()
            user = db.session.query(User).filter_by(email=user_email).first()
            if not user:
                return {"msg": "Unauthorized"}, 401

            if reservation_id:
                try:
                    reservation_id = int(reservation_id)
                    if reservation_id <= 0:
                        return {"msg": "Invalid reservation ID"}, 400
                except ValueError:
                    return {"msg": "Invalid reservation ID"}, 400

                res = db.session.query(Reservation).get(reservation_id)
                if not res:
                    return {"msg": "Reservation not found"}, 404
                if res.user_id != user.id and user.role != 'admin':
                    return {"msg": "Unauthorized access"}, 403
                
                response = {
                    'reservation id': res.id,
                    'spot_id': res.spot_id,
                    'user_id': res.user_id,
                    'lot_id': res.lot_id,
                    'parked at': res.parking_timestamp.isoformat() if res.parking_timestamp else None,
                    'leaving_timestamp': res.leaving_timestamp.isoformat() if res.leaving_timestamp else None,
                    'cost': res.parking_cost
                }
                return response, 200

            # For list of reservations
            if user.role == 'admin':
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                pagination = db.session.query(Reservation).paginate(page=page, per_page=per_page, error_out=False)
                reservations = pagination.items
            else:
                reservations = db.session.query(Reservation).filter_by(user_id=user.id).all()

            result = [{
                'reservation id': res.id,
                'spot_id': res.spot_id,
                'user_id': res.user_id,
                'lot_id': res.lot_id,
                'parked at': res.parking_timestamp.isoformat() if res.parking_timestamp else None,
                'leaving_timestamp': res.leaving_timestamp.isoformat() if res.leaving_timestamp else None,
                'cost': res.parking_cost
            } for res in reservations]
            
            # For admin with pagination, you might want to include pagination info
            if user.role == 'admin':
                return {
                    "reservations": result,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "current_page": pagination.page
                }, 200
            else:
                return {"reservations": result}, 200

        except SQLAlchemyError as e:
            return {"msg": f"Database error: {str(e)}"}, 500
        except Exception as e:
            return {"msg": f"Server error: {str(e)}"}, 500
    @jwt_required
    def post(self):
        try:
            user_email = get_jwt_identity()
            user = User.query.filter_by(email=user_email).first()

            data = request.get_json()
            lot_id = data.get('lot_id')

            if not lot_id:
                return {"msg": "lot_id is required"}, 400

            lot = ParkingLot.query.get(lot_id)
            if not lot or lot.available <= 0:
                return {"msg": "No available spots in this lot"}, 404
            
            spot = ParkingSpot.query.filter_by(lot_id=lot_id, status='A').first()
            if not spot:
                return {"msg": "No available spots in this lot"}, 404

            reservation = Reservation(
                spot_id=spot.id,
                user_id=user.id,
                parking_timestamp=datetime.utcnow()
            )
            spot.status = 'O'
            lot.available -= 1
            db.session.add(reservation)
            db.session.commit()
            cache.delete('AvailableLots')
            return {"msg": "Reservation successful", "reservation_id": reservation.id}, 201
        except Exception as e:
            db.session.rollback()
            print(f"Error in ReservationResource.post: {str(e)}")
            return {"msg": f"Failed to create reservation: {str(e)}"}, 500
   
    @jwt_required
    def put(self, reservation_id):
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()

        res = Reservation.query.get(reservation_id)
        if not res:
            return {"msg": "Reservation not found"}, 404

        if res.user_id != user.email:
            return {"msg": "Unauthorized"}, 403

        res.leaving_timestamp = datetime.utcnow()
        lot = ParkingLot.query.get(res.spot.lot_id)

        duration = (res.leaving_timestamp - res.parking_timestamp).total_seconds() / 3600  # in hours
        res.parking_cost = round(duration * lot.price, 2)
        res.spot.status = 'A'
        lot.available += 1
        cache.delete('AvailableLots')
        db.session.commit()
        return {"msg": "Reservation ended", "cost": res.parking_cost}

    @admin_required
    def delete(self, reservation_id):
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()

        res = Reservation.query.get(reservation_id)
        if not res:
            return {"msg": "Reservation not found"}, 404

        if res.user_id != user.email and user.role!='admin':
            return {"msg": "Unauthorized"}, 403

        lot = ParkingLot.query.get(res.spot.lot_id)
        res.spot.status = 'A'
        lot.available += 1
        cache.delete('AvailableLots')
        db.session.delete(res)
        db.session.commit()
        return {"msg": "Reservation deleted and spot freed"}

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
##switch up the code a bit
class UserResource(Resource):
    @jwt_required()
    def get(self, user_id=None):
        print("JWT Identity:", get_jwt_identity())
        if user_id:
            user = User.query.get(user_id)
            if user:
                return {
                    "msg": "user found",
                    'email': user.email,
                    'name': user.name,
                    'vehicleno': user.vehicleno
                }
            return {"error": "user not found"}, 404
        else:
            current_user = User.query.filter_by(email=get_jwt_identity()).first()
            if not current_user or current_user.role != 'admin':
                return {'msg': "Admin access only"}, 403
            users = User.query.all()
            print("Users queried:", users)  # Debug: Check queried users
            users_list = []
            for user in users:
                user_dict = user.to_dict()
                print("User dict:", user_dict)  # Debug: Check each user dict
                users_list.append(user_dict)
            return {"msg": "all users", "users": users_list}
  
    def post(self):
        data = request.get_json()
        email = data.get('email')
        name = data.get('name')
        password = data.get('password')  
        role = 'user' 

        if not email or not name or not password:
            return {'msg': "Please provide all required information!"}, 400

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return {'msg': "User already exists!"}, 400


        new_user = User(email=email, name=name, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return {'msg': "Successfully registered user!"}, 201

    @jwt_required
    def put(self, user_id=None):
        if not user_id:
            return {'msg': "User id is required to update!"}, 400
        user = User.query.get(user_id)
        if not user:
            return {'msg': "User not exists to update!"}, 404
        data = request.get_json()
        name = data.get('name', None)
        if not name:
            return {'msg': "Please provide all required information!"}, 400
        user.name = name
        db.session.commit()
        user = user.to_dict()
        return {'msg': "User information updated!", 'user': user}, 200
    
    @jwt_required
    def delete(self, user_id=None):
        if not user_id:
            return {'msg': "User id is required to delete!"}, 400
        user = User.query.get(user_id)
        if not user:
            return {'msg': "User not exists to delete!"}, 404
        db.session.delete(user)
        db.session.commit()
        return {'msg': "User has been delete!"}, 200

class SpotResource(Resource):
    @admin_required
    def get(self, lot_id=None, spot_id=None):
        if not spot_id:
            return {'msg': "Spot id is required to get!"}, 400
        # Filter by both lot_id and spot_id to ensure correct spot
        spot = ParkingSpot.query.filter_by(lot_id=int(lot_id), id=int(spot_id)).first()
        if not spot:
            return {'msg': "Spot not exists!"}, 404
        
        spot_data = spot.to_dict()
        # Add user and reservation details for occupied spots
        if spot.status == 'O':
            # Use the reservations relationship to get the first (or active) reservation
            reservation = Reservation.query.filter_by(spot_id=spot.id, leaving_timestamp=None).first()
            if reservation:
                user = User.query.get(reservation.user_id)
                print("Fetched user: ", user)
                if user:
                    spot_data['user'] = {
                        'name': user.name,
                        'email': user.email,
                        'vehicle_number': user.vehicleno  # From User table
                    }
                    spot_data['parking_time'] = reservation.parking_timestamp.isoformat() if hasattr(reservation, 'parking_timestamp') else 'N/A'
                else:
                    spot_data['user'] = None
                    spot_data['parking_time'] = None
        return {'msg': "Spot information", 'spot': spot_data}, 200