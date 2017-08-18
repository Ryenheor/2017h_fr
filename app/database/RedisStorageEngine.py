import redis

from app.database import BaseDB as bdb

class RedisStorageEngine(bdb.BaseDb):
    def connection(self,connect_host, connect_port, connect_db):
        pool = redis.ConnectionPool(host='localhost', port=6379, db='db0')
        r = redis.Redis(connection_pool=pool)
        return r


