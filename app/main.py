import falcon
import redis
import os

#from app.api import LocationResource
from app.database import RedisStorageEngine
from app.api import UserResource as ur, LocationResource as lr, VisitResource as vr
#from app.api import LocationResource

# redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
#host='localhost', port=6379, db='db0'
# conn = redis.from_url(redis_url)


db = RedisStorageEngine.RedisStorageEngine()
api = application = falcon.API()

#api.add_route('/users', ur.UserCollectionResource(db))
api.add_route('/users/{user_id}', ur.UserItemResource(db))
api.add_route('/users/{user_id}/visits', ur.UserItemVisitsResource(db))
api.add_route('/users/new', ur.UserCreateItemResource(db))


# api.add_route('/locations', lr.LocationCollectionResource(db))
# api.add_route('/locations/{location_id}', lr.LocationItemResource(db))
# api.add_route('/locations/{location_id}/avg', lr.LocationCollectionAVGResource(db))
# api.add_route('/locations/new', lr.LocationCreateItemResource(db))
#
#
# api.add_route('/visits', vr.VisitCollectionResource(db))
# api.add_route('/visits/{visit_id}', vr.VisitItemResource(db))
# api.add_route('/visits/new', vr.VisitCreateItemResource(db))


from waitress import serve
serve(api, listen='*:8080')