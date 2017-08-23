from app.helpers import Helper as hlpr

# В User (Профиль) записаны следующие данные:
#
# id - уникальный внешний идентификатор пользователя. Устанавливается тестирующей системой и используется для проверки ответов сервера. 32-разрядное целое беззнаковое число.
# email - адрес электронной почты пользователя. Тип - unicode-строка длиной до 100 символов. Уникальное поле.
# first_name и last_name - имя и фамилия соответственно. Тип - unicode-строки длиной до 50 символов.
# gender - unicode-строка m означает мужской пол, а f - женский.
# birth_date - дата рождения, записанная как число секунд от начала UNIX-эпохи по UTC (другими словами - это timestamp).

class ValidateUser():
    def __init__(self):
        pass

    @classmethod
    def ValidateCreateUser(self,obj):
        try:
            if len(obj['email']) > 100 or len(obj['first_name']) > 50 or len(obj['last_name']) > 50:
                return False
            if obj['gender'] !="m" and obj['gender']!='f':
                return False
            # date = hlpr.convert_date(obj['birth_date'])
            if not hlpr.intTryParse(obj['birth_date']):
                return False
            # if date < dt.datetime(1930, 1, 1) or date > dt.datetime(1999, 1, 1):
            #     return False
            return True
        except:
            return False

    @classmethod
    def ValidateEditUser(self,obj, objold):
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
                # date = hlpr.convert_date(obj['birth_date'])
                # if date < dt.datetime(1930, 1, 1) or date > dt.datetime(1999, 1, 1):
                if not hlpr.intTryParse(obj['birth_date']):
                    return False , None
                else:
                    objold['birth_date'] = obj['birth_date']
            return True, objold
        except:
            return False, None