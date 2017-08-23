from app.helpers import Helper as hlpr

# В Location (Достопримечательность) записаны следующие данные:
#
# id - уникальный внешний id достопримечательности. Устанавливается тестирующей системой. 32-разрядное целое беззнаковоее число.
# place - описание достопримечательности. Текстовое поле неограниченной длины.
# country - название страны расположения. unicode-строка длиной до 50 символов.
# city - название города расположения. unicode-строка длиной до 50 символов.
# distance - расстояние от города по прямой в километрах. 32-разрядное целое беззнаковое число.

class ValidateLocation():
    def __init__(self):
        pass

    @classmethod
    def ValidateCreateLocation(self,obj):
        try:
            if len(obj['country']) > 50 or len(obj['city']) > 50:
                return False
            if not hlpr.intTryParse(obj['distance']):
                return False
            if not obj['place']:
                return False
            return True
        except:
            return False

    @classmethod
    def ValidateEditLocation(self,obj, objold):
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
                if not hlpr.intTryParse(obj['distance']):
                    return False, None
                else:
                    objold['distance'] = obj['distance']

            if 'place'in obj:
                objold['place'] = obj['place']

            return True, objold
        except:
            return False, None