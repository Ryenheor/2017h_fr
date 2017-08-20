# -*- coding: utf8 -*-
import json
import falcon
import datetime as dt
from operator import itemgetter
import pandas as pd
# from rq import Queue
# from rq.job import Job  - это на потом

# id - уникальный внешний идентификатор пользователя. Устанавливается тестирующей системой и используется затем,
# для проверки ответов сервера. 32-разрядное целое число.
# email - адрес электронной почты пользователя. Тип - unicode-строка длиной до 100 символов. Гарантируется уникальность.
# first_name и last_name - имя и фамилия соответственно. Тип - unicode-строки длиной до 50 символов.
# gender - unicode-строка "m" означает мужской пол, а "f" - женский.
# birth_date - дата рождения, записанная как число секунд от начала UNIX-эпохи по UTC (другими словами - это timestamp).
# Ограничено снизу 01.01.1930 и сверху 01.01.1999-ым.
def Validation(obj):
    try:
        if len(obj['email']) > 100 or len(obj['first_name']) > 50 or len(obj['last_name']) > 50:
            return False
        if obj['gender'] !="m" and obj['gender']!='f':
            return False
        date = convert_date(obj['birth_date'])
        print("validate data")
        if date < dt.datetime(1930, 1, 1) or date > dt.datetime(1999, 1, 1):
            print("smth wrong data")
            return False
        return True
    except:
        return False

def ValidationEdit(obj, objold):
    try:
        if "email" in obj:
            if len(obj['email']) > 100:
                return False, None
            else:
                objold['email'] = obj['email']
        if 'first_name' in obj:
            if len(obj['first_name']) > 50:
                return False, None
            else:
                objold['first_name'] = obj['first_name']
        if 'last_name' in obj:
            if len(obj['last_name']) > 50:
                return False, None
            else:
                objold['last_name'] = obj['last_name']
        if 'gender' in obj:
            if obj['gender'] !="m" and obj['gender']!='f':
                return False, None
            else:
                objold['gender'] = obj['gender']

        if 'birth_date' in obj:
            date = convert_date(obj['birth_date'])
            if date < dt.datetime(1930, 1, 1) or date > dt.datetime(1999, 1, 1):
                return False , None
            else:
                objold['birth_date'] = obj['birth_date']
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

class UserItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, user_id):
        try:
            connection = self.db.connection()
            result = connection.get("user:"+user_id)

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


    def on_post(self, req, resp, user_id):
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,'Error',ex.message)
        try:
            result_json = json.loads(raw_json.decode('cp1251'))
            # TODO: получить элемент, и обновить только те поля,которые пришли!
            connection = self.db.connection()
            result = connection.get("user:"+user_id)
            if result is None:
                raise falcon.HTTPError(falcon.HTTP_404,'Not found')
            result = json.loads(result.decode('cp1251'))
            is_valid, updated_result = ValidationEdit(result_json, result)
            if is_valid:
                connection = self.db.connection()
                connection.set("user:"+str(user_id), json.dumps(updated_result, ensure_ascii=False))
            else:
                raise falcon.HTTPError(falcon.HTTP_400,'Validation error')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,'The JSON was incorrect.')


class UserCreateItemResource(object):
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
                connection.set("user:"+str(result_json['id']), json.dumps(result_json, ensure_ascii=False))
            else:
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