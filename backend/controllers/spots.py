from flask_restful import Resource
from models import ParkingSpot, Reservation, User
from decorators import admin_required

class SpotResource(Resource):
    @admin_required
    def get(self, lot_id=None, spot_id=None):
        # Validate and convert IDs
        try:
            lot_id = int(lot_id)
            spot_id = int(spot_id)
        except (ValueError, TypeError):
            return {'msg': "Invalid lot_id or spot_id. Must be integers."}, 400

        if not spot_id:
            return {'msg': "Spot id is required to get!"}, 400

        # Fetch the spot
        spot = ParkingSpot.query.filter_by(lot_id=lot_id, id=spot_id).first()
        if not spot:
            return {'msg': "Spot not found!"}, 404

        # Manually build spot data
        spot_data = {
            'spot_id': spot.id,
            'lot_id': spot.lot_id,
            'status': spot.status,
            'reservation_id': None,
            'user_id': None,
            'user': None,
            'parking_time': None
        }

        # If occupied, fetch reservation and user
        if spot.status == 'O':
            reservation = Reservation.query.filter_by(spot_id=spot.id, leaving_timestamp=None).first()
            if reservation:
                user = User.query.get(reservation.user_id)
                spot_data['reservation_id'] = reservation.id
                spot_data['user_id'] = reservation.user_id
                spot_data['parking_time'] = reservation.parking_timestamp.isoformat() if reservation.parking_timestamp else None
                if user:
                    spot_data['user'] = {
                        'name': user.name,
                        'email': user.email,
                        'vehicle_number': user.vehicleno
                    }

        return {'msg': "Spot information", 'spot': spot_data}, 200
        