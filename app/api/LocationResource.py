# -*- coding: utf8 -*-
import json
import falcon
import datetime as dt
import numpy as np
import math
from operator import itemgetter
import pandas as pd
# from rq import Queue
# from rq.job import Job  - это на потом

# В Location (Достопримечательность) записаны следующие данные:
#
# id - уникальный внешний id достопримечательности. Устанавливается тестирующей системой. 32-разрядное целое беззнаковоее число.
# place - описание достопримечательности. Текстовое поле неограниченной длины.
# country - название страны расположения. unicode-строка длиной до 50 символов.
# city - название города расположения. unicode-строка длиной до 50 символов.
# distance - расстояние от города по прямой в километрах. 32-разрядное целое беззнаковое число.
def Validation(obj):
    try:
        if len(obj['country']) > 50 or len(obj['city']) > 50:
            return False
        if not intTryParse(obj['distance']):
            return False
        if not obj['place']:
            return False
        return True
    except:
        return False

def ValidationEdit(obj, objold):
    try:
        if "country" in obj:
            if len(obj['country']) > 50:
                return False, None
            else:
                objold['country'] = obj['country']

        if "city" in obj:
            if len(obj['city']) > 50:
                return False, None
            else:
                objold['city'] = obj['city']


        if 'distance' in obj:
            if not intTryParse(obj['distance']):
                return False, None
            else:
                objold['distance'] = obj['distance']

        if 'place'in obj:
            objold['place'] = obj['place']

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

class LocationItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, location_id):
        try:
            connection = self.db.connection()
            result = connection.get("location:"+location_id)

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


    def on_post(self, req, resp, location_id):
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,'Error',ex.message)
        try:
            result_json = json.loads(raw_json.decode('cp1251'))
            # TODO: получить элемент, и обновить только те поля,которые пришли!
            connection = self.db.connection()
            result = connection.get("location:"+str(location_id))

            if result is None:
                raise falcon.HTTPError(falcon.HTTP_404,'Not found')
            result = json.loads(result.decode('cp1251'))
            is_valid, updated_result = ValidationEdit(result_json, result)
            if is_valid:
                connection = self.db.connection()
                connection.set("location:"+str(location_id), json.dumps(updated_result, ensure_ascii=False))
            else:
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')


class LocationCreateItemResource(object):
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
                connection.set("location:"+str(result_json['id']), json.dumps(result_json, ensure_ascii=False))
            else:
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')


# Получение средней оценки достопримечательности: /locations/<id>/avg
#
# В ответе ожидается одно число, с точностью до 5 десятичных знаков (округляется по стандартным математическим правилам округления(round)), либо код 404.
# GET-параметры:
#
# fromDate - учитывать оценки только с visited_at > fromDate
# toDate - учитывать оценки только до visited_at < toDate
# fromAge - учитывать только путешественников, у которых возраст (считается от текущего timestamp) строго больше этого параметра
# toAge - учитывать только путешественников, у которых возраст (считается от текущего timestamp) строго меньше этого параметра
# gender - учитывать оценки только мужчин или женщин
#   {
#         "avg": 3.43
#     }
def adapt_locations(items, connection, **params):

    res = []
    for item in items:
        item_obj = item.decode("cp1251")
        item_obj = json.loads(item_obj)
        is_valid = True
        if ("fromDate" in params and item_obj['visited_at']>=int(params["fromDate"])) or \
           ("toDate" in params and item_obj['visited_at']<=int(params["fromDate"])):
            is_valid = False

        if is_valid is True:
            user_item = connection.get("user:"+str(item_obj["user"]))
            user_item = user_item.decode("utf-8")
            #location_item = json.dumps(location_item)
            user_item = json.loads(user_item)


            if ("gender" in params and user_item['gender']==params["gender"]) or \
               ("fromAge" in params and user_item['birth_date']>=int(params["fromAge"])) or \
               ("toAge" in params and user_item['birth_date']<=int(params["toAge"])):
                is_valid = False

            if is_valid is True:
                res.append(item_obj["mark"])
    res = round(np.mean(res),5)
    return {res}


class LocationAVGResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, location_id):
        try:
            connection = self.db.connection()
            keys = connection.keys("visit:*_*_"+location_id)
            vals = connection.mget(keys)

            # TODO: вот эту жесть переписать
            # TODO: сделать валидацию на параметры
            if req.params is not None:
                for key in req.params:
                    if key not in ["fromDate","toDate","fromAge","toAge","gender"]:
                        raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')
                    if key in ["fromDate","toDate","fromAge","toAge"]:
                        if not intTryParse(req.params[key]):
                            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')
            # TODO: получать элементы в зависимости от параметров в url-запросе
            #result  =  list( map(adapt, vals))
            # result = json.dumps(result,ensure_ascii=False)
            result = adapt_locations(items=vals,connection=connection,**req.params)
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