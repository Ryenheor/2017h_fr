# -*- coding: utf8 -*-
import json
import falcon
import datetime as dt
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
        date = dt.datetime.fromtimestamp(obj['birth_date'])
        print("validate data")
        if date < dt.datetime(1930, 1, 1) or date > dt.datetime(1999, 1, 1):
            print("smth wrong data")
            return False
        return True
    except:
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
            if Validation(result_json):
                connection = self.db.connection()
                connection.set("user:"+str(user_id), json.dumps(result_json, ensure_ascii=False))
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
    return x.decode("utf-8")

class UserItemVisitsResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, user_id):
        try:
            connection = self.db.connection()
            keys = connection.keys("visit:*_"+user_id+"_*")
            vals = connection.mget(keys)
            # TODO: переделать чтобы получали данные в нужном формате
            result  =  list( map(adapt, vals))

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