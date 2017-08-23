from app.helpers import Helper as hlpr
from operator import itemgetter
import json

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


class AdaptReturnUser():
    def __init__(self):
        pass

    @classmethod
    def UserVisits(self, items, connection, **params):
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
                location_item = connection.get_by_id("location", item_obj["location"])

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
