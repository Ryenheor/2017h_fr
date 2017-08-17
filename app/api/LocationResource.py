import json
import falcon
# from rq import Queue
# from rq.job import Job

class LocationCollectionResource(object):
    def __init__(self, db):
        self.db = db

    def on_post(self, req, resp):
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Error',
                ex.message)
        try:
            result_json = json.loads(raw_json.decode("utf-8"), encoding='utf-8')
            connection = self.db.connection()
            # парсить
            connection.set("location:"+str(2), result_json)
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Malformed JSON',
                'Could not decode the request body. The JSON was incorrect.')



class LocationItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, location_id):
        try:
            connection = self.db.connection()
        except Exception as ex:
            pass

        result = connection.get("location:"+user_id)
        print (result.decode("utf-8") )
        if result is None:
            resp.body = {}
            resp.status = falcon.HTTP_404

        else:
            resp.body = json.dumps(result.decode("utf-8"),ensure_ascii=False)
            resp.status = falcon.HTTP_200

