import redis

from app.database import BaseDB as bdb

class RedisStorageEngine():
    def connection(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db='db0')
        r = redis.Redis(connection_pool=pool)
        return r


