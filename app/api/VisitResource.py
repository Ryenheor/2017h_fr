# -*- coding: utf8 -*-
import json
import falcon
# from rq import Queue
# from rq.job import Job  - это на потом

class VisitItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, visit_id):
        try:
            result = self.db.get_by_id("visit:_*_*", visit_id)
            if result is None:
                resp.body = json.dumps("{}",ensure_ascii=False)
                resp.status = falcon.HTTP_404
            else:
                resp.body = json.dumps(result, ensure_ascii=False)
                resp.status = falcon.HTTP_200
        except Exception as ex:
             raise falcon.HTTPError(falcon.HTTP_400,'{}')

    def on_post(self, req, resp, visit_id):
         try:
            raw_json = req.stream.read()
            result_json = json.loads(raw_json.decode('cp1251'))
            if not self.db.edit("user", result_json["id"]+"_"+result_json["user"]+"_"+result_json["location"], result_json):
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
         except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')


class VisitCreateItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_post(self, req, resp):
        try:
            raw_json = req.stream.read()
            result_json = json.loads(raw_json.decode('cp1251'))
            if not self.db.create("visit:", result_json["id"]+"_"+result_json["user"]+"_"+result_json["location"]):
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')

