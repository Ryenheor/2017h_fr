# -*- coding: utf8 -*-
import json
import falcon
import datetime as dt
from operator import itemgetter
import pandas as pd
# from rq import Queue
# from rq.job import Job  - это на потом

# В Visit (Посещение) записаны следующие данные:
#
# id - уникальный внешний id посещения. Устанавливается тестирующей системой. 32-разрядное целое беззнакое число.
# location - id достопримечательности. 32-разрядное целое беззнаковое число.
# user - id путешественника. 32-разрядное целое беззнаковое число.
# visited_at - дата посещения, timestamp.
# mark - оценка посещения от 0 до 5 включительно. Целое число.
def Validation(obj):
    try:
        if not intTryParse(obj['mark']) or obj['mark'] < 0 or obj['mark']>5 :
            return False
        if not intTryParse(obj['location']) or not intTryParse(obj['user']):
            return False
        date = convert_date(obj['visited_at'])
        if date < dt.datetime(1930, 1, 1) or date > dt.datetime(1999, 1, 1):
            print("smth wrong data")
            return False
        return True
    except:
        return False

def ValidationEdit(obj, objold):
    try:
        if "mark" in obj:
            if not intTryParse(obj['mark']) or obj['mark'] < 0 or obj['mark']>5 :
                return False, None
            else:
                objold['mark'] = obj['mark']
        if 'location' in obj:
            if not intTryParse(obj['location']):
                return False, None
            else:
                objold['location'] = obj['location']

        if 'user' in obj:
            if not intTryParse(obj['user']):
                return False, None
            else:
                objold['user'] = obj['user']

        if 'visited_at' in obj:
            date = convert_date(obj['visited_at'])
            # if date < dt.datetime(1930, 1, 1) or date > dt.datetime(1999, 1, 1):
            #     return False , None
            # else:
            objold['visited_at'] = obj['visited_at']
        return True, objold
    except:
        return False, None

def convert_date(timestamp_data):
    if timestamp_data < 0:
        return dt.datetime(1970, 1, 1) + dt.timedelta(seconds=timestamp_data)
    else:
        return dt.datetime.utcfromtimestamp(timestamp_data)

def intTryParse(value):
    try:
        res = int(value)
        return True
    except ValueError:
        return False

class VisitItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, visit_id):
        try:
            connection = self.db.connection()
            result = connection.get("visit:"+visit_id)

            try:
                if result is None:
                    resp.body = json.dumps("{}",ensure_ascii=False)
                    resp.status = falcon.HTTP_404
                else:
                    result = result.decode("utf-8")
                    resp.body = json.dumps(result, ensure_ascii=False)
                    resp.status = falcon.HTTP_200
            except Exception as ex:
                raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')

        except Exception as ex:
             raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')


    def on_post(self, req, resp, visit_id):
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,'Error',ex.message)
        try:
            result_json = json.loads(raw_json.decode('cp1251'))
            # TODO: получить элемент, и обновить только те поля,которые пришли!
            connection = self.db.connection()
            result = connection.get("visit:"+result_json["visit_id"])
            if result is None:
                raise falcon.HTTPError(falcon.HTTP_404,'Not found')

            is_valid, updated_result = ValidationEdit(result_json, result)
            if is_valid:
                connection = self.db.connection()
                connection.set("visit:"+str(visit_id), json.dumps(updated_result, ensure_ascii=False))
            else:
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')


class VisitCreateItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_post(self, req, resp):
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,'Error', ex.message)
        try:
            result_json = json.loads(raw_json.decode('cp1251'))
            if Validation(result_json):
                connection = self.db.connection()
                connection.set("visit:"+str(result_json['id']), json.dumps(result_json, ensure_ascii=False))
            else:
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')

