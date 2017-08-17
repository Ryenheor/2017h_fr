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



# class UserCollectionResource(object):
#     def __init__(self, db):
#         self.db = db
#
#     def on_post(self, req, resp):
#         try:
#             raw_json = req.stream.read()
#         except Exception as ex:
#             raise falcon.HTTPError(falcon.HTTP_400,
#                 'Error',
#                 ex.message)
#         try:
#             result_json = json.loads(raw_json.decode("utf-8"), encoding='utf-8')
#             connection = self.db.connection()
#             # парсить
#             connection.set("user:"+result_json['id'], result_json)
#         except ValueError:
#             raise falcon.HTTPError(falcon.HTTP_400,
#                 'Malformed JSON',
#                 'Could not decode the request body. The JSON was incorrect.')



class UserItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, user_id):
        try:
            connection = self.db.connection()
        except Exception as ex:
            pass

        result = connection.get("user:"+user_id)
        # obj = json.load(result)
        # print (result.decode("utf-8") )
        if result is None:
            resp.body = {}
            resp.status = falcon.HTTP_404
        else:
            resp.body = json.dumps(result.decode("utf-8"),ensure_ascii=False)
            resp.status = falcon.HTTP_200

    def on_post(self, req, resp, user_id):
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
            connection.set("user:"+str(result_json['id']), result_json)
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Malformed JSON',
                'Could not decode the request body. The JSON was incorrect.')


class UserCreateItemResource(object):
    def __init__(self, db):
        self.db = db

    def on_post(self, req, resp):
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,'Error', ex.message)
        try:
            # может сломаться
            result_json = json.loads(raw_json.decode("utf-8"), encoding='utf-8')
            connection = self.db.connection()
            print(1)
            # парсить
            connection.set("user:"+str(result_json['id']), result_json)
            # if Validation(result_json):
            #
            #     connection.set("user:"+result_json['id'], result_json)
            # else :
            #     resp.status = falcon.HTTP_400
            #connection.set("user:"+result_json['id'], result_json)
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                'Malformed JSON',
                'Could not decode the request body. The JSON was incorrect.')

class UserItemVisitsResource(object):
    def __init__(self, db):
        self.db = db

    def on_get(self, req, resp, user_id):
        try:
            connection = self.db.connection()
        except Exception as ex:
            pass
        keys = connection.keys("visit:*_"+user_id+"_*")
        vals = connection.mget(keys)
        result  =  list( map(lambda x: x.decode("utf-8"), vals))

        if result is None:
            resp.body = {}
            resp.status = falcon.HTTP_404
        else:
            resp.body = json.dumps(result,ensure_ascii=False)
            resp.status = falcon.HTTP_200