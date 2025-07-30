from flask_restful import Api
from .parking import ParkingResource
from .report import ReportResource
from .spots import SpotResource
from .reservation import ReservationResource
from .users import UserResource, UserSummaryResource, loginResource

def initialize_resources(app):
    api = Api(app)

    api.add_resource(ParkingResource, '/lots', '/lots/<lot_id>')
    api.add_resource(SpotResource,'/lots/<lot_id>/<spot_id>')
    api.add_resource(ReservationResource, '/reservations', '/reservations/<int:reservation_id>')
    api.add_resource(UserResource, '/users', '/users/<int:user_id>')
    api.add_resource(loginResource, '/login')
    api.add_resource(ReportResource, '/report')
    api.add_resource(UserSummaryResource, '/user/charts')


    return api