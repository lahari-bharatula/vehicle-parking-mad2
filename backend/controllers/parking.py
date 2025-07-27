from flask_restful import Resource
from flask import request
from models import ParkingLot, ParkingSpot, Reservation
from extensions import db, cache
from decorators import admin_required
from flask_jwt_extended import jwt_required
from sqlalchemy import select


class ParkingResource(Resource):
    @cache.cached(timeout=60, key_prefix=lambda: f"AvailableLots_{request.view_args.get('lot_id') or 'all'}")
    @jwt_required()
    def get(self, lot_id=None):
        try:
            if lot_id:
                plot = ParkingLot.query.get(lot_id)
                if plot:
                    occupied = ParkingSpot.query.filter_by(lot_id=plot.id, status='O').count()
                    return {
                        'msg': 'lot found',
                        'lot': plot.id,
                        'area': plot.area,
                        'pin_code': plot.pin_code,
                        'available': plot.available,
                        'capacity': plot.capacity,
                        'occupied': occupied,
                        'price': plot.price
                    }, 200
                return {'msg': 'parking lot not found'}, 404

            lots = ParkingLot.query.all()
            lots_data = []
            for lot in lots:
                occupied = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()
                lots_data.append({
                    'lot': lot.id,
                    'area': lot.area,
                    'price': lot.price,
                    'pin_code': lot.pin_code,
                    'available': lot.available,
                    'capacity': lot.capacity,
                    'spots': [{'id': s.id, 'status': s.status} for s in lot.spots],
                    'occupied': occupied
                })
            return {'msg': "all parking lots", "parking_lots": lots_data}, 200
        except Exception as e:
            print(f"Error in ParkingResource.get: {str(e)}")
            return {"msg": f"Failed to fetch lots: {str(e)}"}, 500

    @admin_required
    def post(self):
        data = request.get_json()
        loc = data.get('area')
        price = data.get('price')
        address = data.get('address')
        pin_code = data.get('pin_code')  
        capacity = data.get('capacity')

        if capacity is None or capacity < 0:
            return {"error": "capacity must be provided and non-negative"}, 400
        if not loc or not price or not address or not pin_code:
            return {'msg': "All fields (area, price, address, pin_code, capacity) are required."}, 400

        # Create the lot
        lot = ParkingLot(
            area=loc,
            price=price,
            address=address,
            pin_code=pin_code,
            capacity=capacity,
            available=capacity
        )
        db.session.add(lot)
        db.session.commit()

        # Create parking spots
        for _ in range(capacity):
            db.session.add(ParkingSpot(lot_id=lot.id, status='A'))
        db.session.commit()

        cache.delete_memoized(self.get)  # Clear cache after change
        return {"message": "Parking lot and spots created", "lot_id": lot.id}, 201

    @admin_required
    def put(self, lot_id):
        try:
            cache.delete_memoized(self.get)
            if not lot_id:
                return {"msg": "lot id is required to update"}, 400
            data = request.get_json()
            lot = ParkingLot.query.get_or_404(lot_id)

            new_capacity = data.get('capacity')
            if new_capacity is None or new_capacity < 0:
                return {"msg": "capacity must be non-negative"}, 400

            # Update other fields
            lot.area = data.get('area', lot.area)
            lot.price = data.get('price', lot.price)
            lot.address = data.get('address', lot.address)
            lot.pin_code = data.get('pin_code', lot.pin_code)

            # Sync capacity and spots
            total_spots = ParkingSpot.query.filter_by(lot_id=lot.id).count()
            occupied_spots = ParkingSpot.query.filter_by(lot_id=lot.id, status='O').count()

            if new_capacity < occupied_spots:
                return {"msg": f"Cannot set capacity to {new_capacity}. {occupied_spots} spots are occupied."}, 400

            diff = new_capacity - total_spots
            if diff > 0:
                for _ in range(diff):
                    db.session.add(ParkingSpot(lot_id=lot.id, status='A'))
            elif diff < 0:
                to_remove = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').limit(abs(diff)).all()
                if len(to_remove) < abs(diff):
                    return {"msg": "Not enough available spots to remove"}, 400
                for s in to_remove:
                    db.session.delete(s)

            lot.capacity = new_capacity
            lot.available = new_capacity - occupied_spots
            db.session.commit()
            return {"msg": "Parking lot updated successfully"}, 200
        except Exception as e:
            db.session.rollback()
            return {"msg": f"Failed to update lot: {str(e)}"}, 500

    @admin_required
    def delete(self, lot_id=None):
        try:
            cache.delete_memoized(self.get)
            if not lot_id:
                return {"msg": "lot id is required to delete"}, 400

            lot = ParkingLot.query.get(lot_id)
            if not lot:
                return {"msg": "lot not found"}, 404

            spot_ids = [spot.id for spot in lot.spots]
            active_res = db.session.execute(
                select(Reservation)
                .where(Reservation.spot_id.in_(spot_ids))
                .where(Reservation.leaving_timestamp.is_(None))
            ).scalars().first()

            if active_res:
                return {"msg": "Cannot delete lot with active reservations"}, 400

            db.session.delete(lot)
            db.session.commit()
            return {"msg": "parking lot has been deleted"}, 200
        except Exception as e:
            db.session.rollback()
            return {"msg": f"Failed to delete lot: {str(e)}"}, 500
