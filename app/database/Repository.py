import json

from app.database import RedisStorageEngine as engine
from app.helpers.Validator import Validator as vl
from app.helpers.ReturnAdapter import AdaptReturn as ar


class AbstractRepository:

    def __init__(self):
        pass

    def create(self, obj):
        raise NotImplementedError()

    def edit(self, id, **fields):
        raise NotImplementedError()

    def get_by_id(self,id):
        raise NotImplementedError()

    def get_by_field(self, **fields):
        raise NotImplementedError()


class RedisRepository(AbstractRepository):

    def __init__(self):
        connect = engine.RedisStorageEngine()
        self.db = connect.connection()

    def create(self, table, obj):
        try:
            validator = vl.Validator(table,"create")
            if validator(obj):
                self.db.set(table+":"+str(obj['id']), json.dumps(obj, ensure_ascii=False))
                return True
            else:
                return False
        except Exception as ex:
            raise ValueError

    def edit(self, table, id, fields):
        try:
            pass
            editable = self.get_by_id(table,id)
            if editable is None:
                return False
            editable = json.loads(editable)
            validator = vl.Validator(table,"edit")
            is_valid , result = validator(fields,editable)
            if is_valid:
                self.db.set(table+":"+str(id), json.dumps(result, ensure_ascii=False))
                return True
            else:
                raise ValueError
        except Exception as ex:
            raise ValueError

    def get_by_id(self, table, id):
        try:
            res = self.db.get(table+":"+str(id))
            if res is not None:
                return res.decode("utf-8")
            else:
                return None
        except:
            raise ValueError

    def get_by_field(self, table, mask):
        try:
            keys = self.db.keys(table+":"+mask)
            vals = self.db.mget(keys)
            return vals
        except Exception as ex:
            raise ValueError


# class MySqlRepository(AbstractRepository):
#
#     def __init__(self,db):
#         self.db = db
#
#     def create(self, obj):
#         raise NotImplementedError()
#
#     def edit(self, id, **fields):
#         raise NotImplementedError()
#
#     def get_by_id(self,id):
#         raise NotImplementedError()
#
#     def get_by_field(self, **fields):
#         raise NotImplementedError()
