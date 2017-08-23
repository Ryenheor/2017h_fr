# -*- coding: utf8 -*-
import json
import falcon

from app.helpers import Helper as hlpr
from app.helpers.ReturnAdapter import AdaptReturn as adpt
# import pandas as pd  - это на потом
# from rq import Queue
# from rq.job import Job

class UserItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, user_id):
        try:
            result = self.db.get_by_id("user", user_id)
            if result is None:
                resp.body = json.dumps("{}",ensure_ascii=False)
                resp.status = falcon.HTTP_404
            else:
                resp.body = json.dumps(result, ensure_ascii=False)
                resp.status = falcon.HTTP_200
        except Exception as ex:
             raise falcon.HTTPError(falcon.HTTP_400,'{}')


    def on_post(self, req, resp, user_id):
        try:
            raw_json = req.stream.read()
            result_json = json.loads(raw_json.decode('cp1251'))
            if not self.db.edit("user", user_id, result_json):
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')


class UserCreateItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_post(self, req, resp):
        try:
            raw_json = req.stream.read()
            result_json = json.loads(raw_json.decode('cp1251'))
            if not self.db.create("user", result_json):
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')


class UserItemVisitsResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, user_id):
        try:
            vals = self.db.get_by_field("visit", "*_"+user_id+"_*")

            # TODO: вот эту жесть переписать
            if req.params is not None:
                for key in req.params:
                    if key not in ["fromDate","toDate","country","toDistance"]:
                        raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')
                    if key in ["fromDate","toDate","toDistance"]:
                        if not hlpr.intTryParse(req.params[key]):
                            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')

            adapter = adpt.AdaptReturn("user", "visits")
            result = adapter(items=vals, connection=self.db, **req.params)
            try:
                if result is None:
                    resp.body = json.dumps("{}",ensure_ascii=False)
                    resp.status = falcon.HTTP_404
                else:
                    resp.body = json.dumps(result,ensure_ascii=False)
                    resp.status = falcon.HTTP_200
            except Exception as ex:
                raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')

        except Exception as ex:
             raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')