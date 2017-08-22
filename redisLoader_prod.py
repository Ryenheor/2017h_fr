import redis
import json
import zipfile, glob
import os
import shutil
from shutil import copyfile



if __name__ == '__main__':
    # redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    # conn = redis.from_url(redis_url)
    pool = redis.ConnectionPool(host='localhost', port=6379, db='db0')
    db = redis.Redis(connection_pool=pool)

    THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

    my_file = os.path.join(THIS_FOLDER, 'tmp/data_train.zip')
    folder_name = os.path.join(THIS_FOLDER, 'prod_data')
    # copyfile('/tmp/data/data.zip', my_file)
    shutil.rmtree(folder_name,ignore_errors=True)

    with zipfile.ZipFile(my_file, "r") as z:
        z.extractall(folder_name)

    for file in glob.glob("prod_data/locations*"):
        try:
            with open(file, encoding='utf-8') as data_file:
                data_location = json.load(data_file)
            for location in data_location["locations"]:
                db.set("location:"+str(location['id']), json.dumps(location,ensure_ascii=False))
        except Exception as ex:
            print(ex.message)
    print("locations is done")

    for file in glob.glob("prod_data/users*"):
        try:
            with open(file, encoding='utf-8') as data_file:
                data_user = json.load(data_file)
            for user in data_user["users"]:
                db.set("user:"+str(user['id']), json.dumps(user, ensure_ascii=False))
        except Exception as ex:
            print(ex.message)

    print("users is done")

    for file in glob.glob("prod_data/visits*"):
        try:
            with open(file, encoding='utf-8') as data_file:
                data_visits = json.load(data_file)
            for visit in data_visits["visits"]:
                db.set("visit:"+str(visit['id'])+"_"+str(visit['user'])+"_"+str(visit['location']), json.dumps(visit, ensure_ascii=False))
        except Exception as ex:
                print(file+" file__error parse json")
    print("visits is done")

    shutil.rmtree(folder_name,ignore_errors=True)#