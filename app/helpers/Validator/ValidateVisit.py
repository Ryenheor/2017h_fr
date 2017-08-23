from app.helpers import Helper as hlpr
import datetime as dt

# В Visit (Посещение) записаны следующие данные:
#
# id - уникальный внешний id посещения. Устанавливается тестирующей системой. 32-разрядное целое беззнакое число.
# location - id достопримечательности. 32-разрядное целое беззнаковое число.
# user - id путешественника. 32-разрядное целое беззнаковое число.
# visited_at - дата посещения, timestamp.
# mark - оценка посещения от 0 до 5 включительно. Целое число.

class ValidateVisit():
    def __init__(self):
        pass

    @classmethod
    def ValidateCreateVisit(self,obj):
        try:
            if not hlpr.intTryParse(obj['mark']) or obj['mark'] < 0 or obj['mark']>5 :
                return False
            if not hlpr.intTryParse(obj['location']) or not hlpr.intTryParse(obj['user']):
                return False
            # date = hlpr.convert_date(obj['visited_at'])
            if not hlpr.intTryParse(obj['visited_at']):
            # if date < dt.datetime(1930, 1, 1) or date > dt.datetime(1999, 1, 1):
                return False
            return True
        except:
            return False

    @classmethod
    def ValidateEditUser(self,obj, objold):
        try:
            if "mark" in obj:
                if not hlpr.intTryParse(obj['mark']) or obj['mark'] < 0 or obj['mark']>5 :
                    return False, None
                else:
                    objold['mark'] = obj['mark']
            if 'location' in obj:
                if not hlpr.intTryParse(obj['location']):
                    return False, None
                else:
                    objold['location'] = obj['location']

            if 'user' in obj:
                if not hlpr.intTryParse(obj['user']):
                    return False, None
                else:
                    objold['user'] = obj['user']

            if 'visited_at' in obj:
                # date = hlpr.convert_date(obj['visited_at'])
                if not hlpr.intTryParse(obj['visited_at']):
                # if date < dt.datetime(1930, 1, 1) or date > dt.datetime(1999, 1, 1):
                     return False , None
                else:
                    objold['visited_at'] = obj['visited_at']

            return True, objold
        except:
            return False, None


