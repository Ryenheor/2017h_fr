# -*- coding: utf8 -*-
import json
import falcon
from operator import itemgetter
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



# Получение списка мест, которые посетил пользователь: /users/<id>/visits.
# В теле ответа ожидается структура {"visits": [ ... ]}, отсортированная по возрастанию дат, или ошибка 404/400. Подробнее - в примере.
# Возможные GET-параметры:
# fromDate - посещения с visited_at > fromDate
# toDate - посещения с visited_at < toDate
# country - название страны, в которой находятся интересующие достопримечательности
# toDistance - возвращать только те места, у которых расстояние от города меньше этого параметра
# Пример корректного ответа на запрос:
#
# GET: /users/1/visits
# {
#     "visits": [
#         {
#             "mark": 2,
#             "visited_at": 1223268286,
#             "place": "Кольский полуостров"
#         },
#         {
#             "mark": 4,
#             "visited_at": 958656902,
#             "place": "Московский Кремль"
#         },
#         ...
#      ]
# }
def adapt(x):
    return x.decode("cp1251")

# fromDate - посещения с visited_at > fromDate
# toDate - посещения до visited_at < toDate
# country - название страны, в которой находятся интересующие достопримечательности
# toDistance - возвращать только те места, у которых расстояние от города меньше этого параметра
#, *params
def adapt_visits(items, connection, **params):

    res = {}
    res["visits"] = []
    for item in items:
        item_obj = item.decode("cp1251")
        item_obj = json.loads(item_obj)
        is_valid = True
        if ("fromDate" in params and item_obj['visited_at']>=int(params["fromDate"])) or \
           ("toDate" in params and item_obj['visited_at']<=int(params["fromDate"])):
            is_valid = False

        if is_valid is True:
            location_item = connection.get("location:"+str(item_obj["location"]))
            location_item = location_item.decode("utf-8")
            #location_item = json.dumps(location_item)
            location_item = json.loads(location_item)


            if ("country" in params and location_item['country']==params["country"]) or \
               ("toDistance" in params and location_item['distance']>=int(params["toDistance"])):
                is_valid = False

            if is_valid is True:
                elem = {}
                elem["mark"] = item_obj["mark"]
                elem["visited_at"] = int(item_obj["visited_at"])
                elem["place"] = location_item["place"]
                res["visits"].append(elem)
    # TODO: отсортировать по возрастанию дат

    res["visits"] = sorted(res["visits"], key=itemgetter('visited_at'))
    return res


class UserItemVisitsResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, user_id):
        try:
            connection = self.db.connection()
            keys = connection.keys("visit:*_"+user_id+"_*")
            vals = connection.mget(keys)

            # TODO: вот эту жесть переписать
            # TODO: сделать валидацию на параметры
            if req.params is not None:
                for key in req.params:
                    if key not in ["fromDate","toDate","country","toDistance"]:
                        raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')
                    if key in ["fromDate","toDate","toDistance"]:
                        if not intTryParse(req.params[key]):
                            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')
            # TODO: получать элементы в зависимости от параметров в url-запросе
            #result  =  list( map(adapt, vals))
            # result = json.dumps(result,ensure_ascii=False)
            result = adapt_visits(items=vals,connection=connection,**req.params)
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