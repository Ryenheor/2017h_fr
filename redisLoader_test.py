import redis
import json
import os
import datetime
import pickle

def Validation(obj):
    try:
        if len(obj['email']) > 100 or len(obj['first_name']) > 50 or len(obj['last_name']) > 50:
            return False
        if obj['gender'] !="m" and obj['gender']!='f':
            return False
        date = datetime.datetime.fromtimestamp(obj['birth_date'])
        if date < datetime.datetime(1930, 1, 1) or date > datetime.datetime(1999, 1, 1):
            return False
        return True
    except Exception:
        print(Exception)
        return False


if __name__ == '__main__':
    # redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    # conn = redis.from_url(redis_url)
    pool = redis.ConnectionPool(host='localhost', port=6379, db='db0')
    db = redis.Redis(connection_pool=pool)
    # таким образом можно добавить новый элемент
    #вонзить из json



    # get_script = """
    # local keys = (redis.call('keys', ARGV[1]))
    # local values={}
    #
    # for i,key in ipairs(keys) do
    #     local val = redis.call('GET', key)
    #     values[i]=val
    #     i=i+1
    # end
    #
    # return values
    # """
    # get_values = db.register_script(get_script)
    #
    # print (get_values(args=["visit:*_1_*"]))
    #kv = db.mget("visit:*_1_*")
    #result = db.keys("visit:*_1_*")
    #result = db.scan_iter(match='visit:*_1_*')

    # keys = db.keys("visit:*_1_*")
    # vals = db.mget(keys)
    # print(vals)
    # smth  =  list( map(lambda x: x.decode("utf-8"), vals))
    # print (smth)

    # jso = pickle.loads(result)


    with open('data/locations_1.json', encoding='utf-8') as data_file:
        data_location = json.load(data_file)


    for location in data_location["locations"]:
        db.set("location:"+str(location['id']), json.dumps(location,ensure_ascii=False))
    print("locations is done")
    #
    with open('data/users_1.json', encoding='utf-8') as data_file:
        data_user = json.load(data_file)

    for user in data_user["users"]:
        #print(Validation(user))

        db.set("user:"+str(user['id']), json.dumps(user, ensure_ascii=False))

    print("users is done")
    #
    with open('data/visits_1.json', encoding='utf-8') as data_file:
        data_visits = json.load(data_file)

    for visit in data_visits["visits"]:
        db.set("visit:"+str(visit['id'])+"_"+str(visit['user'])+"_"+str(visit['location']), json.dumps(visit, ensure_ascii=False))

    print("visits is done")

#