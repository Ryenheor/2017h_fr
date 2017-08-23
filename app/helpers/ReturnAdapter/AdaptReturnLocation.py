from app.helpers import Helper as hlpr
import json
import datetime as dt
import numpy as np
from dateutil.relativedelta import relativedelta
import calendar

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

class AdaptReturnLocation():
    def __init__(self):
        pass

    @classmethod
    def LocationAVG(self, items, connection, **params):
        res = []
        for item in items:
            item_obj = item.decode("cp1251")
            item_obj = json.loads(item_obj)
            is_valid = True

            if "fromDate" in params or "toDate" in params:
                now = dt.datetime.now() - relativedelta(years = int(params["fromDate"]))
                timestampFrom = calendar.timegm(now.timetuple())

                now2 = dt.datetime.now() - relativedelta(years = int(params["toDate"]))
                timestampTo = calendar.timegm(now2.timetuple())

                if ("fromDate" in params and item_obj['visited_at']>timestampFrom) or \
                   ("toDate" in params and item_obj['visited_at']<timestampTo):
                    is_valid = False

            if is_valid is True:
                #user_item = connection.get("user:"+str(item_obj["user"]))
                user_item = connection.get_by_id("user", item_obj["user"])
                #user_item = user_item.decode("utf-8")
                #location_item = json.dumps(location_item)
                user_item = json.loads(user_item)

                if ("gender" in params and user_item['gender']==params["gender"]) or \
                   ("fromAge" in params and user_item['birth_date']>=int(params["fromAge"])) or \
                   ("toAge" in params and user_item['birth_date']<=int(params["toAge"])):
                    is_valid = False

                if is_valid is True:
                    res.append(item_obj["mark"])
        res = round(np.mean(res),5)
        return {"avg":res}