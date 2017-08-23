# -*- coding: utf8 -*-
import json
import falcon

from app.helpers import Helper as hlpr
from app.helpers.ReturnAdapter import AdaptReturn as adpt
import pandas as pd
# from rq import Queue
# from rq.job import Job  - это на потом

class LocationItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, location_id):
        try:
            result = self.db.get_by_id("location", location_id)
            if result is None:
                resp.body = json.dumps("{}",ensure_ascii=False)
                resp.status = falcon.HTTP_404
            else:
                resp.body = json.dumps(result, ensure_ascii=False)
                resp.status = falcon.HTTP_200
        except Exception as ex:
             raise falcon.HTTPError(falcon.HTTP_400,'{}')


    def on_post(self, req, resp, location_id):
        try:
            raw_json = req.stream.read()
            result_json = json.loads(raw_json.decode('cp1251'))
            if not self.db.edit("location", location_id, result_json):
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')


class LocationCreateItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_post(self, req, resp):
        try:
            raw_json = req.stream.read()
            result_json = json.loads(raw_json.decode('cp1251'))
            if not self.db.create("location", result_json):
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')



class LocationAVGResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, location_id):
        try:
            vals = self.db.get_by_field("visit", "*_*_"+location_id)
            # TODO: вот эту жесть переписать
            if req.params is not None:
                for key in req.params:
                    if key not in ["fromDate","toDate","fromAge","toAge","gender"]:
                        raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')
                    if key in ["fromDate","toDate","fromAge","toAge"]:
                        if not hlpr.intTryParse(req.params[key]):
                            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')

            adapter = adpt.AdaptReturn("location", "avg")
            result = adapter(items=vals,connection=self.db, **req.params)
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