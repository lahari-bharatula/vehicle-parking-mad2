from datetime import datetime
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from extensions import db, cache
from models import ParkingLot, ParkingSpot, Reservation,User
from decorators import admin_required
from sqlalchemy.exc import SQLAlchemyError

class ReservationResource(Resource):
    @jwt_required()
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
                    'reservation_id': res.id,
                    'spot_id': res.spot_id,
                    'user_id': res.user_id,
                    'lot_id': res.lot_id,
                    'parked_at': res.parking_timestamp.isoformat() if res.parking_timestamp else None,
                    'leaving_timestamp': res.leaving_timestamp.isoformat() if res.leaving_timestamp else None,
                    'cost': res.parking_cost
                }
                return response, 200

            # No reservation_id → list reservations
            if user.role == 'admin':
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 10, type=int)
                pagination = db.session.query(Reservation).paginate(page=page, per_page=per_page, error_out=False)
                reservations = pagination.items
            else:
                reservations = db.session.query(Reservation).filter_by(user_id=user.id).all()

            result = [{
                'reservation_id': res.id,
                'spot_id': res.spot_id,
                'user_id': res.user_id,
                'lot_id': res.lot_id,
                'parked_at': res.parking_timestamp.isoformat() if res.parking_timestamp else None,
                'leaving_timestamp': res.leaving_timestamp.isoformat() if res.leaving_timestamp else None,
                'cost': res.parking_cost
            } for res in reservations]
            
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

    @jwt_required()
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
                lot_id=lot.id,
                user_id=user.id,
                parking_timestamp=datetime.utcnow()
            )
            spot.status = 'O'
            lot.available -= 1
            db.session.add(reservation)
            db.session.commit()
            cache.delete('AvailableLots')
            return {"msg": "Reservation successful", "reservation_id": reservation.id}, 201
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"msg": f"Database error: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"msg": f"Failed to create reservation: {str(e)}"}, 500

    @jwt_required()
    def put(self, reservation_id):
        try:
            user_email = get_jwt_identity()
            user = User.query.filter_by(email=user_email).first()

            res = Reservation.query.get(reservation_id)
            if not res:
                return {"msg": "Reservation not found"}, 404

            if res.user_id != user.id and user.role != 'admin':
                return {"msg": "Unauthorized"}, 403

            if res.leaving_timestamp:
                return {"msg": "Reservation already ended"}, 400

            res.leaving_timestamp = datetime.utcnow()
            lot = ParkingLot.query.get(res.lot_id)

            duration = (res.leaving_timestamp - res.parking_timestamp).total_seconds() / 3600
            res.parking_cost = round(duration * lot.price, 2)
            res.spot.status = 'A'
            lot.available += 1
            cache.delete('AvailableLots')
            db.session.commit()
            return {"msg": "Reservation ended", "cost": res.parking_cost}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"msg": f"Database error: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"msg": f"Server error: {str(e)}"}, 500

    @admin_required
    def delete(self, reservation_id):
        try:
            res = Reservation.query.get(reservation_id)
            if not res:
                return {"msg": "Reservation not found"}, 404

            lot = ParkingLot.query.get(res.lot_id)
            res.spot.status = 'A'
            lot.available += 1
            cache.delete('AvailableLots')
            db.session.delete(res)
            db.session.commit()
            return {"msg": "Reservation deleted and spot freed"}
        except SQLAlchemyError as e:
            db.session.rollback()
            return {"msg": f"Database error: {str(e)}"}, 500
        except Exception as e:
            db.session.rollback()
            return {"msg": f"Server error: {str(e)}"}, 500
