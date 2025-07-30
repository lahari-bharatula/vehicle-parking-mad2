import os
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from TasksCelery import generate_csv
from models import Reservation, User


class ReportResource(Resource):
    @jwt_required()
    def get(self):
        user_email = get_jwt_identity()
        user = User.query.filter_by(email=user_email).first()
        if not user:
            return {"error": "User not found"}, 404

        user_id = user.id
        reservations = Reservation.query.filter_by(user_id=user_id).all()

        if not reservations:
            return {"msg": "No reservations found"}, 404

        # Convert reservations to list of dicts for JSON-safe Celery args
        reservations_data = []
        for res in reservations:
            reservations_data.append({
                'id': res.id,
                'spot_id': res.spot_id,
                'lot_id': res.lot_id,
                'parking_timestamp': res.parking_timestamp.isoformat() if res.parking_timestamp else '',
                'leaving_timestamp': res.leaving_timestamp.isoformat() if res.leaving_timestamp else '',
                'parking_cost': res.parking_cost,
                'remarks': getattr(res, 'remarks', '')
            })

        # Set file path
        cwd = os.getcwd()
        static_path = os.path.join(cwd, "static")
        os.makedirs(static_path, exist_ok=True)
        filename = f"report_{user_id}.csv"
        filepath = os.path.join(static_path, filename)

        # Trigger async CSV generation
        generate_csv.delay(reservations_data, filepath)

        return {
            "msg": "Generating file... check back soon.",
            "url": f"http://localhost:5000/static/{filename}"
        }, 200