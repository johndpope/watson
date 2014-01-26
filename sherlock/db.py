from pymongo import MongoClient, GEO2D
import cfg
import datetime
from bson.son import SON

client = MongoClient(cfg.DB_CONF["host"], cfg.DB_CONF["port"]).watson



class DBConnector():
    def __init__(self):
        pass

    def add_user(self, external_id, access_token):

        cursor = client.users.find({"external_id": external_id})
        if cursor.count() > 0:
            return client.users.update({
                                           "external_id": external_id}, {
                                           "$set": {"access_token": access_token}
                                       })
        else:
            return client.users.insert({
                "external_id": external_id,
                "access_token": access_token,
                "cursor": None
            })

    def update_cursor(self, user_id, cursor):
        client.users.update({"_id": user_id},
                            {"$set": {"cursor": cursor}})

    def delete_user(self, user_id):
        client.users.remove({"_id": user_id})

    def get_user(self, external_id):
        return client.users.find_one({"external_id": external_id})

    def get_all_users(self):
        return client.users.find({})

    def insert_image(self, user_id, filename, coords, external_ref, hash, timestamp, group, quality, is_duplicate=False, is_deleted=False):
        if not isinstance(timestamp, datetime.datetime):
            raise RuntimeError
        client.images.ensure_index([("geo", GEO2D)])
        id = client.images.insert({
                                      "user_id": user_id,
                                      "filename": filename,
                                      "geo": coords,
                                      "external_ref": external_ref,
                                      "hash": str(hash),
                                      "timestamp": timestamp,
                                      "group": group,
                                      "quality": quality,
                                      "is_duplicate": is_duplicate,
				                      "is_deleted":is_deleted
                                  }, upsert=True)
        return id


    def get_images_detailed(self, user_id, start_time=None,end_time=None, coords = None):

        search_dict = {"user_id":user_id,"is_duplicate":False}
        if coords and coords[0] and coords[1]:
            search_dict["geo"] = SON([("$near",coords),("$maxDistance",0.5)])

        if start_time and end_time:
            search_dict["timestamp"] = {"$gt":start_time,"$lt":end_time}

        #search_dict['quality'] = {"$gt": 0.45}

        return client.images.find(search_dict)

    def get_images(self, user_id=None, hash=None, group=None, is_duplicate=False):
        if user_id is None and hash is None:
            raise RuntimeError
        srch = {"is_duplicate": is_duplicate}
        if user_id is not None:
            srch["user_id"] = user_id
        if hash is not None:
            srch["hash"] = hash
        if group is not None:
            srch["group"] = group

        return client.images.find(srch)

    def mark_image_duplicate(self, image_id):
        client.images.update({"_id": image_id}, {"$set": {"is_duplicate": True}})


    def find_images_since(self, user_id, from_date, to_date):
	client.images.find({"user_id":user_id,
			    "timestamp":{"$gt":from_date,"$lt":to_date}})

    def find_images_near(self, user_id, coords=[0, 0], distance=0):
        if len(coords) != 2:
            raise RuntimeError
        cur = client.images.find({
            "user_id": user_id,
            "is_duplicate":False,
        })
        return cur

    def get_images_all(self):
        return client.images.find()

    def get_highest_group(self):
	result = [x for x in client.images.find()]
        if len(result) == 0:
            return 0
        else:
            return int(client.images.find({}).sort("group", -1).limit(1)[0]['group'])

if __name__ == "__main__":
    conn = DBConnector()
    client.users.drop()
    client.images.drop()

    conn.add_user("exx", "sess")
    conn.add_user("exx", "cccc")

    bb = conn.get_user("exx")

    import pdb;

    pdb.set_trace()

